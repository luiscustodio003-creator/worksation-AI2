"""Scheduler do Runtime Engine (hardening 07 — Fase 8.5).

Implementação pesada do kernel (KERNEL-09): vive em ``wsai2.infrastructure``,
por trás do contrato público `wsai2.runtime_engine`, que re-exporta o
``Scheduler``.

Determina a ordem de execução de planos de forma determinística e executa-os
através do ``RuntimeManager``. A via histórica permanece directa e sequencial
por omissão; a fila multicamada é uma camada aditiva e opt-in.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Callable, Mapping, Sequence

from wsai2.core.public import ExecutionContext, ExecutionPriority, ValidationError
from wsai2.security import PolicyEngine

from .base_runtime import ExecutionReport, ScheduleOutcome, SchedulerReport, StepRunner
from .manager import RuntimeManager
from .queue import MultilayerExecutionQueue

if TYPE_CHECKING:
    from wsai2.execution import RecoveryPolicy, TimeoutPolicy
    from wsai2.task import ExecutionPlan
    from .monitoring import ExecutionMonitor

_PRIORIDADE_ORDEM: dict[ExecutionPriority, int] = {
    ExecutionPriority.CRITICAL: 0,
    ExecutionPriority.HIGH: 1,
    ExecutionPriority.NORMAL: 2,
    ExecutionPriority.LOW: 3,
}


class Scheduler:
    """Agenda e executa planos por prioridade determinística."""

    def __init__(
        self,
        manager: RuntimeManager,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._manager = manager
        self._clock = clock

    def run(
        self,
        plans: Sequence[ExecutionPlan],
        *,
        priorities: Mapping[str, ExecutionPriority] | None = None,
        context_factory: Callable[[ExecutionPlan], ExecutionContext] | None = None,
        timeout: TimeoutPolicy | None = None,
        recovery: RecoveryPolicy | None = None,
        policy: PolicyEngine | None = None,
        stop_on_failure: bool = False,
        monitor: ExecutionMonitor | None = None,
        concurrency: int = 1,
        step_runner: StepRunner | None = None,
        queue: MultilayerExecutionQueue[ExecutionPlan] | None = None,
    ) -> SchedulerReport:
        """Executa planos directamente ou através de uma fila multicamada.

        ``queue=None`` preserva exactamente a via histórica. Quando uma fila
        é fornecida, os planos são admitidos na camada pronta/backlog e
        consumidos pela mesma semântica de execução do scheduler. A fila só
        preempta itens ainda pendentes; trabalho já iniciado nunca é
        interrompido por esta camada.
        """
        if (
            not isinstance(concurrency, int)
            or isinstance(concurrency, bool)
            or concurrency < 1
        ):
            raise ValidationError(
                "concurrency tem de ser um inteiro >= 1",
                code="wsai.runtime.concurrency",
            )
        prioridades: Mapping[str, ExecutionPriority] = priorities or {}

        def _chave(plano: ExecutionPlan) -> int:
            return _PRIORIDADE_ORDEM.get(
                prioridades.get(plano.task_id, ExecutionPriority.NORMAL),
                _PRIORIDADE_ORDEM[ExecutionPriority.NORMAL],
            )

        if queue is None:
            ordem = sorted(plans, key=_chave)
        else:
            queue.enqueue_many(
                (plano, prioridades.get(plano.task_id, ExecutionPriority.NORMAL))
                for plano in plans
            )
            drenados: list[ExecutionPlan] = []
            while (plano := queue.pop_next()) is not None:
                drenados.append(plano)
            ordem = drenados

        inicio = self._clock()
        if monitor is not None:
            monitor.on_schedule_started()

        if concurrency == 1:
            resultados = self._agendar_sequencial(
                ordem,
                prioridades,
                context_factory,
                timeout,
                recovery,
                policy,
                stop_on_failure,
                monitor,
                step_runner,
            )
        else:
            resultados = self._agendar_paralelo(
                ordem,
                prioridades,
                context_factory,
                timeout,
                recovery,
                policy,
                stop_on_failure,
                monitor,
                concurrency,
                step_runner,
            )

        relatorio_final = SchedulerReport(
            outcomes=tuple(resultados),
            order=tuple(resultado.task_id for resultado in resultados),
            duration=self._clock() - inicio,
        )
        if monitor is not None:
            monitor.on_schedule_finished(relatorio_final)
        return relatorio_final

    def _agendar_sequencial(
        self,
        ordem: Sequence[ExecutionPlan],
        prioridades: Mapping[str, ExecutionPriority],
        context_factory: Callable[[ExecutionPlan], ExecutionContext] | None,
        timeout: TimeoutPolicy | None,
        recovery: RecoveryPolicy | None,
        policy: PolicyEngine | None,
        stop_on_failure: bool,
        monitor: ExecutionMonitor | None,
        step_runner: StepRunner | None,
    ) -> list[ScheduleOutcome]:
        resultados: list[ScheduleOutcome] = []
        for plano in ordem:
            contexto = None
            if context_factory is not None:
                contexto = context_factory(plano)
            relatorio: ExecutionReport = self._manager.execute_plan(
                plano,
                contexto,
                step_runner=step_runner,
                timeout=timeout,
                recovery=recovery,
                policy=policy,
                monitor=monitor,
            )
            prioridade = prioridades.get(plano.task_id, ExecutionPriority.NORMAL)
            resultados.append(
                ScheduleOutcome(
                    task_id=plano.task_id,
                    priority=prioridade,
                    report=relatorio,
                )
            )
            if stop_on_failure and not relatorio.is_success:
                break
        return resultados

    def _agendar_paralelo(
        self,
        ordem: Sequence[ExecutionPlan],
        prioridades: Mapping[str, ExecutionPriority],
        context_factory: Callable[[ExecutionPlan], ExecutionContext] | None,
        timeout: TimeoutPolicy | None,
        recovery: RecoveryPolicy | None,
        policy: PolicyEngine | None,
        stop_on_failure: bool,
        monitor: ExecutionMonitor | None,
        concurrency: int,
        step_runner: StepRunner | None,
    ) -> list[ScheduleOutcome]:
        total = len(ordem)
        contextos: list[ExecutionContext | None] = [None] * total
        for posicao, plano in enumerate(ordem):
            if context_factory is not None:
                contextos[posicao] = context_factory(plano)
            else:
                contextos[posicao] = ExecutionContext(
                    execution_id=f"exec-{plano.task_id}-{posicao}",
                    task_id=plano.task_id,
                )

        vistos: set[str] = set()
        for contexto in contextos:
            if contexto is None:
                continue
            if contexto.execution_id in vistos:
                raise ValidationError(
                    "execution_ids duplicados num agendamento paralelo",
                    code="wsai.runtime.duplicate_execution",
                    details={"execution_id": contexto.execution_id},
                )
            vistos.add(contexto.execution_id)

        executados: list[ExecutionReport | None] = [None] * total
        parado = threading.Event()

        def _trabalho(posicao: int) -> None:
            if stop_on_failure and parado.is_set():
                return
            relatorio = self._manager.execute_plan(
                ordem[posicao],
                contextos[posicao],
                step_runner=step_runner,
                timeout=timeout,
                recovery=recovery,
                policy=policy,
                monitor=monitor,
            )
            executados[posicao] = relatorio
            if stop_on_failure and not relatorio.is_success:
                parado.set()

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futuros = [executor.submit(_trabalho, posicao) for posicao in range(total)]
            for futuro in futuros:
                futuro.result()

        resultados: list[ScheduleOutcome] = []
        for posicao, plano in enumerate(ordem):
            relatorio = executados[posicao]
            if relatorio is None:
                continue
            resultados.append(
                ScheduleOutcome(
                    task_id=plano.task_id,
                    priority=prioridades.get(plano.task_id, ExecutionPriority.NORMAL),
                    report=relatorio,
                )
            )
        return resultados


__all__ = ["Scheduler"]
