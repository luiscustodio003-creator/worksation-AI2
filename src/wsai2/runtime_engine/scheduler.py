"""Scheduler do Runtime Engine (hardening 07 — Fase 8.5).

Determina a ordem de execução de um conjunto de planos de forma
**determinística** (por prioridade, estável dentro da mesma prioridade) e
executa-os em sequência através do ``RuntimeManager``, recolhendo um
relatório agregado (``SchedulerReport``).

O scheduler distingue-se do gestor: o gestor executa um plano; o
scheduler decide **a ordem** e percorre os planos. A concorrência entre
planos e filas de espera multicamadas pertencem a uma unidade posterior —
esta unidade mantém um agendamento simples, sequencial e verificável.

Na Fase 8.9 (Gate de addons), o scheduler passa a propagar o motor de
política (8.8) ao gestor: o contrato de composição estabelece que quem
cria o ``RuntimeManager``/``Scheduler`` fornece o ``PolicyEngine`` real,
sendo o scheduler o ponto de instituição junto da fila de agendamento.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

from wsai2.core.context import ExecutionContext, ExecutionPriority
from wsai2.security import PolicyEngine

from .base import ExecutionReport, ScheduleOutcome, SchedulerReport
from .manager import RuntimeManager

if TYPE_CHECKING:
    from wsai2.execution import RecoveryPolicy, TimeoutPolicy
    from wsai2.task import ExecutionPlan
    from .monitoring import ExecutionMonitor

# Ordem de serviço por prioridade (determinística; valores menores
# executam primeiro).
_PRIORIDADE_ORDEM: dict[ExecutionPriority, int] = {
    ExecutionPriority.CRITICAL: 0,
    ExecutionPriority.HIGH: 1,
    ExecutionPriority.NORMAL: 2,
    ExecutionPriority.LOW: 3,
}


class Scheduler:
    """Agenda e executa planos em sequência, por prioridade determinística.

    A instância é stateless: mantém apenas uma referência ao gestor que
    executa os planos.
    """

    def __init__(
        self,
        manager: RuntimeManager,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Cria um scheduler sobre um gestor de execução.

        Args:
            manager: gestor que executa cada plano.
            clock: relógio monotónico para medir durações (injectável).
        """
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
    ) -> SchedulerReport:
        """Executa os planos na ordem determinada por prioridade.

        A ordenação é estável: dentro da mesma prioridade, os planos
        mantêm a ordem fornecida.

        Args:
            plans: planos a executar.
            priorities: prioridade por task_id (por omissão, NORMAL).
            context_factory: constrói o contexto de execução de um plano;
                se omissa, o gestor cria os contextos por omissão.
            timeout: política de timeout aplicada a cada plano (opcional).
            recovery: política de recuperação aplicada a cada plano
                (opcional).
            policy: motor de política (8.8) propagado ao gestor — a
                autorização aplica-se a cada plano **antes do passo 1**
                (Gate de addons, 8.9). Sem motor, nenhuma autorização é
                aplicada (comportamento preservado).
            stop_on_failure: interrompe o agendamento na primeira falha.
            monitor: monitor de execução (unidade residual da Fase 8)
                propagado ao gestor e alimentado com os marcos do
                agendamento; sem monitor, nenhuma observação contínua é
                feita (comportamento preservado).

        Returns:
            O relatório do agendamento, com a ordem efectiva e os
            resultados por plano.
        """
        prioridades: Mapping[str, ExecutionPriority] = priorities or {}

        def _chave(plano: ExecutionPlan) -> int:
            return _PRIORIDADE_ORDEM.get(
                prioridades.get(plano.task_id, ExecutionPriority.NORMAL),
                _PRIORIDADE_ORDEM[ExecutionPriority.NORMAL],
            )

        ordem = sorted(plans, key=_chave)
        resultados: list[ScheduleOutcome] = []
        inicio = self._clock()
        if monitor is not None:
            monitor.on_schedule_started()

        for plano in ordem:
            contexto = None
            if context_factory is not None:
                contexto = context_factory(plano)
            relatorio: ExecutionReport = self._manager.execute_plan(
                plano,
                contexto,
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

        relatorio_final = SchedulerReport(
            outcomes=tuple(resultados),
            order=tuple(resultado.task_id for resultado in resultados),
            duration=self._clock() - inicio,
        )
        if monitor is not None:
            monitor.on_schedule_finished(relatorio_final)
        return relatorio_final


__all__ = ["Scheduler"]