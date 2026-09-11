"""Testes dos endpoints de execução, estado e cancelamento (Fase 10, API-09).

Cobrem os handlers ``execution_start``, ``execution_status`` e
``execution_cancel`` (apresentadores finos dos use-cases APP-10): parsing
do corpo JSON, serialização JSON do plano/relatório/snapshot, serviço
injectável para determinismo, pedidos inválidos (400), e o transporte
stdlib real sobre ``http.server`` (200 / 400 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

import pytest

from wsai2.api import (
    ApiRequest,
    StdLibHttpGateway,
    execution_cancel,
    execution_start,
    execution_status,
)
from wsai2.application import (
    CancellationService,
    ExecutionRequest,
    ExecutionService,
    ExecutionStatusService,
)
from wsai2.runtime_engine import ExecutionMonitor, ExecutionReport, ExecutionStatus
from wsai2.task import ExecutionPlan, Task, TaskKind


def _corpo_tarefa_chat() -> dict[str, object]:
    return {
        "task_id": "t1",
        "kind": "chat",
        "prompt": "Olá!",
        "max_tokens": 256,
        "required_capabilities": ["local_llm_inference"],
    }


def _tarefa_chat() -> Task:
    return Task(
        id="t1",
        kind=TaskKind.CHAT,
        prompt="Olá!",
        max_tokens=256,
        required_capabilities=("local_llm_inference",),
    )


def _plano_executavel() -> ExecutionPlan:
    return ExecutionPlan(
        task_id="t1",
        category="chat",
        feasible=True,
        model_id="m1",
        provider_id="p1",
        reasons=("recursos suficientes",),
        steps=("gerar resposta",),
    )


def _plano_inviavel() -> ExecutionPlan:
    return ExecutionPlan(
        task_id="t1",
        category="chat",
        feasible=False,
        model_id=None,
        provider_id=None,
        reasons=("sem fornecedor saudavel",),
        steps=(),
    )


class _AnaliseFixa:
    """Análise determinista que devolve sempre o mesmo plano."""

    def __init__(self, plano: ExecutionPlan) -> None:
        self._plano = plano

    def resolve(self, request: Any) -> Any:
        return type("R", (), {"plan": self._plano})()


def _relatorio_ok(execution_id: str = "exec-1") -> ExecutionReport:
    return ExecutionReport(
        execution_id=execution_id,
        task_id="t1",
        status=ExecutionStatus.SUCCESS,
        steps=(),
        duration=0.001,
    )


class _GestorFixo:
    """Gestor de execução determinista para testes."""

    def __init__(self, report: ExecutionReport | None = None) -> None:
        self._report = report or _relatorio_ok()

    def execute_plan(self, plano, monitor=None):
        if monitor is not None:
            monitor.on_execution_started(self._report.execution_id, plano.task_id)
            monitor.on_execution_finished(self._report)
        self.executados = getattr(self, "executados", 0) + 1
        return self._report


def _servico_execucao_fixo(
    plano: ExecutionPlan, gestor: _GestorFixo | None = None
) -> ExecutionService:
    return ExecutionService(
        manager_source=lambda: gestor or _GestorFixo(),
        analysis=_AnaliseFixa(plano),
    )


@pytest.fixture()
def gateway_http() -> tuple[StdLibHttpGateway, str, int]:
    gateway = StdLibHttpGateway()
    host, port = gateway.serve("127.0.0.1", 0)
    yield gateway, host, port
    gateway.shutdown()


def _requisicao(
    base: str,
    rota: str,
    metodo: str = "POST",
    corpo: str | None = None,
) -> tuple[int, dict[str, object]]:
    pedido = urllib.request.Request(f"{base}{rota}", method=metodo)
    if corpo is not None:
        dados = corpo.encode("utf-8")
        pedido.add_header("Content-Type", "application/json")
        pedido.data = dados
    try:
        with urllib.request.urlopen(pedido, timeout=15) as resposta:
            return resposta.status, json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read().decode("utf-8"))


# ------------------------------------------------------------------
# POST /executions
# ------------------------------------------------------------------

def test_execution_start_directo_serializavel() -> None:
    """API-09: ``execution_start`` devolve a execução em JSON puro (200)."""
    resposta = execution_start(
        ApiRequest(method="POST", path="/executions", body=json.dumps(_corpo_tarefa_chat()))
    )
    assert resposta.status == 200
    assert set(resposta.payload) == {"task_id", "plan", "report"}
    assert resposta.payload["task_id"] == "t1"
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_execution_start_plano_inviavel_nao_executa() -> None:
    """API-09: plano inviável devolve plano sem relatório."""
    resposta = execution_start(
        ApiRequest(method="POST", path="/executions", body=json.dumps(_corpo_tarefa_chat())),
        service=_servico_execucao_fixo(_plano_inviavel()),
    )
    assert resposta.status == 200
    assert resposta.payload["task_id"] == "t1"
    assert resposta.payload["report"] is None
    plano = resposta.payload["plan"]
    assert isinstance(plano, dict)
    assert plano["feasible"] is False
    assert plano["is_executable"] is False


def test_execution_start_com_servico_injectado_executa() -> None:
    """API-09: plano executável devolve relatório do gestor injectado."""
    gestor = _GestorFixo()
    resposta = execution_start(
        ApiRequest(method="POST", path="/executions", body=json.dumps(_corpo_tarefa_chat())),
        service=_servico_execucao_fixo(_plano_executavel(), gestor),
    )
    assert resposta.status == 200
    assert resposta.payload["task_id"] == "t1"
    assert resposta.payload["plan"] is not None
    relatorio = resposta.payload["report"]
    assert isinstance(relatorio, dict)
    assert relatorio["execution_id"] == "exec-1"
    assert relatorio["task_id"] == "t1"
    assert relatorio["status"] == "success"
    assert isinstance(relatorio["steps"], list)
    assert isinstance(relatorio["duration"], float)
    assert gestor.executados == 1


def test_execution_start_prioridade_e_timeout_aceites() -> None:
    """API-09: prioridade e timeout são aceites no corpo JSON."""
    corpo = {**_corpo_tarefa_chat(), "priority": "high", "timeout_seconds": 30}
    gestor = _GestorFixo()
    resposta = execution_start(
        ApiRequest(method="POST", path="/executions", body=json.dumps(corpo)),
        service=_servico_execucao_fixo(_plano_executavel(), gestor),
    )
    assert resposta.status == 200
    assert gestor.executados == 1


def test_execution_start_kind_invalido_devolve_400() -> None:
    """API-09: um ``kind`` desconhecido é rejeitado com 400."""
    corpo = {**_corpo_tarefa_chat(), "kind": "mágico"}
    resposta = execution_start(
        ApiRequest(method="POST", path="/executions", body=json.dumps(corpo))
    )
    assert resposta.status == 400
    assert "kind invalido" in resposta.payload["error"]


def test_execution_start_body_mal_formado_devolve_400() -> None:
    """API-09: um corpo não-JSON é rejeitado com 400."""
    resposta = execution_start(
        ApiRequest(method="POST", path="/executions", body="isto não é JSON{")
    )
    assert resposta.status == 400
    assert "JSON" in resposta.payload["error"]


# ------------------------------------------------------------------
# POST /executions/status
# ------------------------------------------------------------------

def test_execution_status_sem_execucoes_conhecidas() -> None:
    """API-09: sem registos, o estado fica vazio e tipado."""
    resposta = execution_status(
        ApiRequest(
            method="POST",
            path="/executions/status",
            body=json.dumps({"execution_id": "nada"}),
        ),
        service=ExecutionStatusService(),
    )
    assert resposta.status == 200
    assert resposta.payload["execution_id"] == "nada"
    assert resposta.payload["status"] is None
    assert resposta.payload["snapshot"] is None
    assert resposta.payload["report"] is None


def test_execution_status_execucao_concluida() -> None:
    """API-09: execução concluída expõe estado e relatório."""
    monitor = ExecutionMonitor()
    servico_exec = ExecutionService(
        manager_source=lambda: _GestorFixo(_relatorio_ok()),
        monitor=monitor,
        analysis=_AnaliseFixa(_plano_executavel()),
    )
    servico_exec.resolve(ExecutionRequest(task=_tarefa_chat()))
    resposta = execution_status(
        ApiRequest(
            method="POST",
            path="/executions/status",
            body=json.dumps({"execution_id": "exec-1"}),
        ),
        service=ExecutionStatusService(monitor_source=lambda: monitor),
    )
    assert resposta.status == 200
    assert resposta.payload["status"] == "success"
    assert isinstance(resposta.payload["report"], dict)
    assert resposta.payload["snapshot"] is None


def test_execution_status_sem_id_devolve_400() -> None:
    """API-09: falta de ``execution_id`` é rejeitada com 400."""
    resposta = execution_status(
        ApiRequest(method="POST", path="/executions/status", body=json.dumps({}))
    )
    assert resposta.status == 400
    assert "execution_id obrigatorio" in resposta.payload["error"]


# ------------------------------------------------------------------
# POST /executions/cancel
# ------------------------------------------------------------------

def test_execution_cancel_sem_fonte_devolve_false() -> None:
    """API-09: por omissão, o cancelamento devolve cancelled=False."""
    resposta = execution_cancel(
        ApiRequest(
            method="POST",
            path="/executions/cancel",
            body=json.dumps({"execution_id": "exec-1"}),
        ),
        service=CancellationService(),
    )
    assert resposta.status == 200
    assert resposta.payload == {
        "execution_id": "exec-1",
        "cancelled": False,
    }


def test_execution_cancel_com_fonte_injectada() -> None:
    """API-09: com fonte injectada, o cancelamento é aplicado."""
    resposta = execution_cancel(
        ApiRequest(
            method="POST",
            path="/executions/cancel",
            body=json.dumps({"execution_id": "exec-1"}),
        ),
        service=CancellationService(cancel_source=lambda _: True),
    )
    assert resposta.status == 200
    assert resposta.payload["cancelled"] is True


def test_execution_cancel_sem_id_devolve_400() -> None:
    """API-09: falta de ``execution_id`` é rejeitada com 400."""
    resposta = execution_cancel(
        ApiRequest(method="POST", path="/executions/cancel", body=json.dumps({}))
    )
    assert resposta.status == 400
    assert "execution_id obrigatorio" in resposta.payload["error"]


# ------------------------------------------------------------------
# Transporte HTTP
# ------------------------------------------------------------------

def test_execution_start_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(
        f"http://{host}:{port}",
        "/executions",
        corpo=json.dumps(_corpo_tarefa_chat()),
    )
    assert status == 200
    assert "task_id" in payload
    assert "plan" in payload
    assert "report" in payload


def test_execution_cancel_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(
        f"http://{host}:{port}",
        "/executions/cancel",
        corpo=json.dumps({"execution_id": "exec-1"}),
    )
    assert status == 200
    assert payload["execution_id"] == "exec-1"
    assert payload["cancelled"] is False


def test_execution_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/executions", metodo="GET")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}