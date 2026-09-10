"""Testes dos use-cases de Execução, Estado e Cancelamento (APP-10).

Verifica que os serviços compõem a execução observada do
``wsai2.runtime_engine`` (gestor/monitor injectáveis) e que o
cancelamento só tem efeito com fonte injectada — sem implementar o motor
nem conhecer fornecedores.
"""

from dataclasses import FrozenInstanceError

from typing import Any

import pytest

from wsai2.application import (
    CancellationRequest,
    CancellationResponse,
    CancellationService,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionService,
    ExecutionStatusRequest,
    ExecutionStatusResponse,
    ExecutionStatusService,
)
from wsai2.runtime_engine import (
    ExecutionMonitor,
    ExecutionReport,
    ExecutionSnapshot,
    ExecutionStatus,
)
from wsai2.task import ExecutionPlan, Task, TaskKind


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


def test_execute_padrao_devolve_plano_e_relatorio() -> None:
    """APP-10: a execução devolve plano e relatório do gestor injetado."""
    gestor = _GestorFixo()
    servico = ExecutionService(
        manager_source=lambda: gestor,
        analysis=_AnaliseFixa(_plano_executavel()),
    )
    resposta = servico.resolve(ExecutionRequest(task=_tarefa_chat()))
    assert isinstance(resposta, ExecutionResponse)
    assert resposta.task_id == "t1"
    assert resposta.plan is not None
    assert resposta.report is not None
    assert resposta.report.status is ExecutionStatus.SUCCESS
    assert gestor.executados == 1


def test_execute_mantem_plano_sem_relatorio_quando_inviavel() -> None:
    """APP-10: plano inviável não é executado (sem relatório)."""
    tarefa = Task(
        id="t2",
        kind=TaskKind.CHAT,
        prompt="Olá!",
        required_capabilities=("capacidade_impossivel",),
    )
    servico = ExecutionService(manager_source=lambda: _GestorFixo())
    resposta = servico.resolve(ExecutionRequest(task=tarefa))
    assert resposta.plan is not None
    assert resposta.plan.is_executable is False
    assert resposta.report is None


def test_estado_sem_execucoes_conhecidas() -> None:
    """APP-10: sem registos, o estado fica vazio e tipado."""
    servico = ExecutionStatusService()
    resposta = servico.resolve(ExecutionStatusRequest(execution_id="nada"))
    assert isinstance(resposta, ExecutionStatusResponse)
    assert resposta.status is None
    assert resposta.snapshot is None
    assert resposta.report is None


def test_estado_de_execucao_em_curso() -> None:
    """APP-10: execução em curso expõe a fotografia (snapshot)."""
    monitor = ExecutionMonitor()
    monitor.on_execution_started("exec-1", "t1")
    servico = ExecutionStatusService(monitor_source=lambda: monitor)
    resposta = servico.resolve(ExecutionStatusRequest(execution_id="exec-1"))
    assert isinstance(resposta.snapshot, ExecutionSnapshot)
    assert resposta.snapshot.running is True
    assert resposta.report is None


def test_estado_de_execucao_concluida() -> None:
    """APP-10: execução concluída expõe estado e relatório."""
    monitor = ExecutionMonitor()
    servico_exec = ExecutionService(
        manager_source=lambda: _GestorFixo(_relatorio_ok()),
        monitor=monitor,
        analysis=_AnaliseFixa(_plano_executavel()),
    )
    servico_exec.resolve(ExecutionRequest(task=_tarefa_chat()))
    servico = ExecutionStatusService(monitor_source=lambda: monitor)
    resposta = servico.resolve(ExecutionStatusRequest(execution_id="exec-1"))
    assert resposta.status is ExecutionStatus.SUCCESS
    assert resposta.report is not None
    assert resposta.snapshot is None


def test_cancelamento_sem_fonte_nao_produz_efeito() -> None:
    """APP-10: por omissão, o cancelamento devolve cancelled=False."""
    resposta = CancellationService().resolve(
        CancellationRequest(execution_id="exec-1")
    )
    assert resposta == CancellationResponse(execution_id="exec-1", cancelled=False)


def test_cancelamento_com_fonte_injectada() -> None:
    """APP-10: com fonte injectada, o efeito é aplicado."""
    resposta = CancellationService(cancel_source=lambda _: True).resolve(
        CancellationRequest(execution_id="exec-1")
    )
    assert resposta.cancelled is True


def test_respostas_imutaveis_a_contrato() -> None:
    """APP-10: as respostas respeitam o contrato congelado."""
    servico = ExecutionStatusService()
    resposta = servico.resolve(ExecutionStatusRequest(execution_id="exec-1"))
    with pytest.raises(FrozenInstanceError):
        resposta.execution_id = "outra"

    cancelamento = CancellationService().resolve(
        CancellationRequest(execution_id="exec-1")
    )
    with pytest.raises(FrozenInstanceError):
        cancelamento.cancelled = True