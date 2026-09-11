"""Endpoint de análise de tarefas da API (API-07).

Apresenta o use-case ``TaskAnalysisService`` (APP-08) sobre HTTP:
transforma o ``TaskAnalysisResponse`` da camada Application num
``ApiResponse`` com payload serializável em JSON (classificação,
requisitos, selecção de capacidades e plano de execução). O handler é
um apresentador fino — não contém lógica de domínio nem I/O próprio:
delega a recolha no serviço, que pode ser injectado para testes
deterministas. Dependência arquitectural: ``api -> application``.

Diferente dos endpoints GET existentes, ``/tasks`` aceita ``POST`` com
um corpo JSON que descreve a tarefa a analisar (``kind``, ``prompt``,
``max_tokens``, ``required_capabilities``).
"""

from __future__ import annotations

import json

from wsai2.application import (
    TaskAnalysisRequest,
    TaskAnalysisResponse,
    TaskAnalysisService,
)
from wsai2.task import Task, TaskKind

from .contract import ApiRequest, ApiResponse

_KIND_MAP: dict[str, TaskKind] = {kind.value: kind for kind in TaskKind}


def tasks(
    request: ApiRequest,
    service: TaskAnalysisService | None = None,
) -> ApiResponse:
    """Endpoint ``POST /tasks``: análise completa de uma tarefa.

    Recebe o corpo JSON com a descrição da tarefa, constrói o
    ``TaskAnalysisRequest``, e devolve a análise serializada em JSON.
    Um ``TaskAnalysisService`` pode ser injectado para testes
    deterministas. O método/rota são validados pelo gateway; aqui
    assume-se ``POST /tasks`` já resolvido.
    """
    dados = _parsear_body(request)
    if isinstance(dados, ApiResponse):
        return dados

    tarefa = _construir_tarefa(dados)
    if isinstance(tarefa, ApiResponse):
        return tarefa

    servico = service if service is not None else TaskAnalysisService()
    resposta: TaskAnalysisResponse = servico.resolve(TaskAnalysisRequest(task=tarefa))
    return ApiResponse(status=200, payload=_analise_para_payload(resposta))


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
    """Constrói uma ``Task`` a partir dos dados do pedido."""
    kind_str = dados.get("kind", "")
    kind = _KIND_MAP.get(str(kind_str))
    if kind is None:
        return ApiResponse(
            status=400,
            payload={"error": f"kind invalido: {kind_str!r}. Valores aceites: {', '.join(_KIND_MAP)}"},
        )

    task_id = dados.get("task_id", dados.get("id", ""))
    prompt = dados.get("prompt", "")
    max_tokens = dados.get("max_tokens", 256)
    required_capabilities = dados.get("required_capabilities", [])
    metadata = dados.get("metadata", {})

    try:
        return Task(
            id=str(task_id),
            kind=kind,
            prompt=str(prompt),
            max_tokens=int(max_tokens),
            required_capabilities=tuple(str(c) for c in required_capabilities),
            metadata={str(k): str(v) for k, v in metadata.items()},
        )
    except (ValueError, TypeError) as exc:
        return ApiResponse(status=400, payload={"error": f"tarefa invalida: {exc}"})


def _analise_para_payload(resposta: TaskAnalysisResponse) -> dict[str, object]:
    """Serializa o ``TaskAnalysisResponse`` em JSON puro."""
    payload: dict[str, object] = {
        "task_id": resposta.task_id,
        "classification": {
            "task_id": resposta.classification.task_id,
            "kind": resposta.classification.kind.value,
            "category": resposta.classification.category.value,
        },
        "requirements": {
            "task_id": resposta.requirements.task_id,
            "category": resposta.requirements.category.value,
            "required_capabilities": list(resposta.requirements.required_capabilities),
            "max_tokens": resposta.requirements.max_tokens,
        },
    }
    if resposta.selection is not None:
        payload["selection"] = {
            "task_id": resposta.selection.task_id,
            "required": list(resposta.selection.required),
            "available": list(resposta.selection.available),
            "missing": list(resposta.selection.missing),
            "is_viable": resposta.selection.is_viable,
        }
    else:
        payload["selection"] = None

    if resposta.plan is not None:
        payload["plan"] = {
            "task_id": resposta.plan.task_id,
            "category": resposta.plan.category,
            "feasible": resposta.plan.feasible,
            "model_id": resposta.plan.model_id,
            "provider_id": resposta.plan.provider_id,
            "reasons": list(resposta.plan.reasons),
            "steps": list(resposta.plan.steps),
            "is_executable": resposta.plan.is_executable,
        }
    else:
        payload["plan"] = None

    return payload
