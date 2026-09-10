"""Serviços dos use-cases de Execução, Estado e Cancelamento (APP-10).

Montam as respostas (contrato APP-02) a partir de ``wsai2.runtime_engine``
(reutilizando o plano da análise ``wsai2.task`` quando executável) — a
Application compõe a execução observada, sem implementar o motor de
execução nem conhecer fornecedores. O cancelamento não tem motor no
runtime_engine actual (Kernel congelado); a fonte é injectável e, por
omissão, não produz efeito.
"""

from __future__ import annotations

from typing import Callable

from wsai2.runtime_engine import (
    ExecutionMonitor,
    ExecutionReport,
    RuntimeManager,
)

from .contract import (
    CancellationRequest,
    CancellationResponse,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatusRequest,
    ExecutionStatusResponse,
    TaskAnalysisRequest,
)
from .tasks_uc import TaskAnalysisService

ManagerSource = Callable[[], RuntimeManager]
CancelSource = Callable[[str], bool]
MonitorSource = Callable[[], ExecutionMonitor]


class ExecutionService:
    """Resolve o use-case de execução de plano (APP-10)."""

    def __init__(
        self,
        manager_source: ManagerSource | None = None,
        monitor: ExecutionMonitor | None = None,
        analysis: TaskAnalysisService | None = None,
    ) -> None:
        self._manager_source = (
            manager_source if manager_source is not None else RuntimeManager
        )
        self._monitor = monitor
        self._analysis = analysis if analysis is not None else TaskAnalysisService()

    def resolve(self, request: ExecutionRequest) -> ExecutionResponse:
        """Executa o plano da tarefa quando executável; senão, devolve sem
        relatório."""
        plano = self._analysis.resolve(
            TaskAnalysisRequest(task=request.task)
        ).plan
        if plano is None or not plano.is_executable:
            return ExecutionResponse(task_id=request.task.id, plan=plano)
        relatorio = self._manager_source().execute_plan(
            plano, monitor=self._monitor
        )
        return ExecutionResponse(
            task_id=request.task.id, plan=plano, report=relatorio
        )


class ExecutionStatusService:
    """Resolve o use-case de estado de execução (APP-10)."""

    def __init__(
        self, monitor_source: MonitorSource | None = None
    ) -> None:
        self._monitor_source = (
            monitor_source if monitor_source is not None else ExecutionMonitor
        )

    def resolve(
        self, request: ExecutionStatusRequest
    ) -> ExecutionStatusResponse:
        """Devolve o estado da execução conhecida do monitor."""
        foto = self._monitor_source().snapshot()
        em_curso = next(
            (
                cada
                for cada in foto.running
                if cada.execution_id == request.execution_id
            ),
            None,
        )
        concluida = next(
            (
                cada
                for cada in foto.finished
                if cada.execution_id == request.execution_id
            ),
            None,
        )
        if concluida is not None:
            return ExecutionStatusResponse(
                execution_id=request.execution_id,
                status=concluida.status,
                report=concluida,
            )
        if em_curso is not None:
            return ExecutionStatusResponse(
                execution_id=request.execution_id, snapshot=em_curso
            )
        return ExecutionStatusResponse(execution_id=request.execution_id)


class CancellationService:
    """Resolve o use-case de cancelamento de execução (APP-10).

    O motor actual do ``runtime_engine`` não expõe cancelamento por
    identificador (Kernel congelado); com uma fonte injectável, o efeito é
    delegado; por omissão, devolve ``cancelled=False`` (sem efeito).
    """

    def __init__(self, cancel_source: CancelSource | None = None) -> None:
        self._cancel_source = (
            cancel_source if cancel_source is not None else lambda _: False
        )

    def resolve(self, request: CancellationRequest) -> CancellationResponse:
        """Devolve o cancelamento aplicado pela fonte configurada."""
        return CancellationResponse(
            execution_id=request.execution_id,
            cancelled=self._cancel_source(request.execution_id),
        )