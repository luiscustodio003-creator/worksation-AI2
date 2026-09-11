"""Endpoints de execução, estado e cancelamento da API (API-09).

Apresenta os use-cases ``ExecutionService``, ``ExecutionStatusService`` e
``CancellationService`` (APP-10) sobre HTTP: transforma as respostas da
camada Application em ``ApiResponse`` com payload serializável em JSON.
Os handlers são apresentadores finos — delegam nos serviços injectáveis e
não contêm lógica de domínio nem I/O próprio.

Três rotas, três handlers (todas POST com corpo JSON, como em API-07/08):

- ``POST /executions`` — submete uma tarefa para execução.
- ``POST /executions/status`` — consulta o estado de uma execução.
- ``POST /executions/cancel`` — cancela uma execução.
"""

from __future__ import annotations

import json

from wsai2.application import (
    CancellationRequest,
    CancellationService,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatusRequest,
    ExecutionStatusResponse,
    ExecutionStatusService,
    ExecutionService,
)
from wsai2.core.public import ExecutionPriority
from wsai2.task import Task, TaskKind

from .contract import ApiRequest, ApiResponse

_PRIORITY_MAP: dict[str, ExecutionPriority] = {
    p.value: p for p in ExecutionPriority
}

_KIND_MAP: dict[str, TaskKind] = {k.value: k for k in TaskKind}


# ------------------------------------------------------------------
# POST /executions
# ------------------------------------------------------------------

def execution_start(
    request: ApiRequest,
    service: ExecutionService | None = None,
) -> ApiResponse:
    """Endpoint ``POST /executions``: submete uma tarefa para execução.

    Recebe o corpo JSON com a descrição da tarefa (``task_id``, ``kind``,
    ``prompt``, ``max_tokens``, ``required_capabilities``) e opções de
    execução (``priority``, ``timeout_seconds``). Devolve o plano e o
    relatório da execução, quando a tarefa é executável.
    """
    dados = _parsear_body(request)
    if isinstance(dados, ApiResponse):
        return dados

    tarefa = _construir_tarefa(dados)
    if isinstance(tarefa, ApiResponse):
        return tarefa

    pedido = _construir_execution_request(dados, tarefa)
    if isinstance(pedido, ApiResponse):
        return pedido

    servico = service if service is not None else ExecutionService()
    resposta: ExecutionResponse = servico.resolve(pedido)
    return ApiResponse(status=200, payload=_execution_para_payload(resposta))


def _parsear_body(request: ApiRequest) -> dict[str, object] | ApiResponse:
    """Extrai e valida o corpo JSON do pedido."""
    if not request.body.strip():
        return ApiResponse(status=400, payload={"error": "body vazio: JSON esperado"})
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return ApiResponse(status=400, payload={"error": "body invalido: JSON esperado"})
    if not isinstance(dados, dict):
        return ApiResponse(status=400, payload={"error": "body invalido: objecto JSON esperado"})
    return dados


def _construir_tarefa(dados: dict[str, object]) -> Task | ApiResponse:
    """Constrói o ``Task`` a partir dos dados do pedido."""
    try:
        kind_valor = str(dados.get("kind", ""))
        kind = _KIND_MAP.get(kind_valor)
        if kind is None:
            return ApiResponse(
                status=400,
                payload={
                    "error": (
                        f"kind invalido: {kind_valor!r}. "
                        f"Valores aceites: {', '.join(_KIND_MAP)}"
                    )
                },
            )
        tarefa = Task(
            id=str(dados.get("task_id", "")),
            kind=kind,
            prompt=str(dados.get("prompt", "")),
            max_tokens=int(dados.get("max_tokens", 256)),
            required_capabilities=tuple(
                str(c) for c in dados.get("required_capabilities", ())
            ),
        )
    except (TypeError, ValueError) as exc:
        return ApiResponse(status=400, payload={"error": f"tarefa invalida: {exc}"})
    return tarefa


def _construir_execution_request(
    dados: dict[str, object], tarefa: Task
) -> ExecutionRequest | ApiResponse:
    """Constrói o ``ExecutionRequest`` a partir dos dados do pedido."""
    try:
        priority_valor = str(dados.get("priority", "normal"))
        priority = _PRIORITY_MAP.get(priority_valor, ExecutionPriority.NORMAL)
        timeout_raw = dados.get("timeout_seconds")
        timeout_seconds: float | None = (
            float(timeout_raw) if timeout_raw is not None else None
        )
        return ExecutionRequest(
            task=tarefa,
            priority=priority,
            timeout_seconds=timeout_seconds,
        )
    except (TypeError, ValueError) as exc:
        return ApiResponse(status=400, payload={"error": f"pedido invalido: {exc}"})


def _execution_para_payload(resposta: ExecutionResponse) -> dict[str, object]:
    """Serializa o ``ExecutionResponse`` em JSON puro."""
    payload: dict[str, object] = {"task_id": resposta.task_id}
    payload["plan"] = _plano_para_payload(resposta.plan) if resposta.plan is not None else None
    payload["report"] = _relatorio_para_payload(resposta.report) if resposta.report is not None else None
    return payload


# ------------------------------------------------------------------
# POST /executions/status
# ------------------------------------------------------------------

def execution_status(
    request: ApiRequest,
    service: ExecutionStatusService | None = None,
) -> ApiResponse:
    """Endpoint ``POST /executions/status``: consulta o estado de uma execução.

    Recebe o corpo JSON com o ``execution_id`` e devolve o estado global,
    a fotografia em curso e/ou o relatório final, quando conhecidos.
    """
    dados = _parsear_body(request)
    if isinstance(dados, ApiResponse):
        return dados

    execution_id = str(dados.get("execution_id", "")).strip()
    if not execution_id:
        return ApiResponse(status=400, payload={"error": "execution_id obrigatorio"})

    try:
        pedido = ExecutionStatusRequest(execution_id=execution_id)
    except (TypeError, ValueError) as exc:
        return ApiResponse(status=400, payload={"error": f"pedido invalido: {exc}"})

    servico = service if service is not None else ExecutionStatusService()
    resposta: ExecutionStatusResponse = servico.resolve(pedido)
    return ApiResponse(status=200, payload=_status_para_payload(resposta))


# ------------------------------------------------------------------
# POST /executions/cancel
# ------------------------------------------------------------------

def execution_cancel(
    request: ApiRequest,
    service: CancellationService | None = None,
) -> ApiResponse:
    """Endpoint ``POST /executions/cancel``: cancela uma execução.

    Recebe o corpo JSON com o ``execution_id`` e devolve se o cancelamento
    foi aplicado. Por omissão, sem fonte injectada, devolve
    ``cancelled=False`` (sem efeito).
    """
    dados = _parsear_body(request)
    if isinstance(dados, ApiResponse):
        return dados

    execution_id = str(dados.get("execution_id", "")).strip()
    if not execution_id:
        return ApiResponse(status=400, payload={"error": "execution_id obrigatorio"})

    try:
        pedido = CancellationRequest(execution_id=execution_id)
    except (TypeError, ValueError) as exc:
        return ApiResponse(status=400, payload={"error": f"pedido invalido: {exc}"})

    servico = service if service is not None else CancellationService()
    resposta = servico.resolve(pedido)
    return ApiResponse(
        status=200,
        payload={"execution_id": resposta.execution_id, "cancelled": resposta.cancelled},
    )


# ------------------------------------------------------------------
# Serialização
# ------------------------------------------------------------------

def _plano_para_payload(plano: object) -> dict[str, object]:
    """Serializa um ``ExecutionPlan`` em JSON puro.

    Usa duck typing (atributos/valores do contrato), sem importar tipos de
    domínio — padrão de API-02..06, sem arestas novas.
    """
    return {
        "task_id": plano.task_id,  # type: ignore[attr-defined]
        "category": plano.category,  # type: ignore[attr-defined]
        "feasible": plano.feasible,  # type: ignore[attr-defined]
        "model_id": plano.model_id,  # type: ignore[attr-defined]
        "provider_id": plano.provider_id,  # type: ignore[attr-defined]
        "reasons": list(plano.reasons),  # type: ignore[attr-defined]
        "steps": list(plano.steps),  # type: ignore[attr-defined]
        "is_executable": plano.is_executable,  # type: ignore[attr-defined]
    }


def _relatorio_para_payload(relatorio: object) -> dict[str, object]:
    """Serializa um ``ExecutionReport`` em JSON puro (duck typing)."""
    erro = relatorio.error  # type: ignore[attr-defined]
    return {
        "execution_id": relatorio.execution_id,  # type: ignore[attr-defined]
        "task_id": relatorio.task_id,  # type: ignore[attr-defined]
        "status": relatorio.status.value,  # type: ignore[attr-defined]
        "steps": [_passo_para_payload(passo) for passo in relatorio.steps],  # type: ignore[attr-defined]
        "duration": relatorio.duration,  # type: ignore[attr-defined]
        "error": _erro_para_payload(erro) if erro is not None else None,
    }


def _passo_para_payload(passo: object) -> dict[str, object]:
    """Serializa um ``StepOutcome`` em JSON puro (duck typing)."""
    erro = passo.error  # type: ignore[attr-defined]
    return {
        "index": passo.index,  # type: ignore[attr-defined]
        "step": passo.step,  # type: ignore[attr-defined]
        "status": passo.status.value,  # type: ignore[attr-defined]
        "duration": passo.duration,  # type: ignore[attr-defined]
        "error": _erro_para_payload(erro) if erro is not None else None,
    }


def _erro_para_payload(erro: object) -> dict[str, object]:
    """Serializa um ``WsaiError`` em JSON puro."""
    return {
        "code": getattr(erro, "code", "wsai.error"),
        "message": str(erro),
        "details": dict(getattr(erro, "details", {})),
    }


def _status_para_payload(resposta: ExecutionStatusResponse) -> dict[str, object]:
    """Serializa o ``ExecutionStatusResponse`` em JSON puro."""
    payload: dict[str, object] = {"execution_id": resposta.execution_id}
    payload["status"] = resposta.status.value if resposta.status is not None else None
    payload["snapshot"] = _snapshot_para_payload(resposta.snapshot) if resposta.snapshot is not None else None
    payload["report"] = _relatorio_para_payload(resposta.report) if resposta.report is not None else None
    return payload


def _snapshot_para_payload(snapshot: object) -> dict[str, object]:
    """Serializa um ``ExecutionSnapshot`` em JSON puro (duck typing)."""
    return {
        "execution_id": snapshot.execution_id,  # type: ignore[attr-defined]
        "task_id": snapshot.task_id,  # type: ignore[attr-defined]
        "running": snapshot.running,  # type: ignore[attr-defined]
        "started_at": snapshot.started_at,  # type: ignore[attr-defined]
        "elapsed": snapshot.elapsed,  # type: ignore[attr-defined]
        "current_step": snapshot.current_step,  # type: ignore[attr-defined]
        "current_step_name": snapshot.current_step_name,  # type: ignore[attr-defined]
    }


__all__ = ["execution_start", "execution_status", "execution_cancel"]