"""Scheduler do Runtime Engine (hardening 07 — Fase 8.5).

Determina a ordem de execução de um conjunto de planos de forma
**determinística** (por prioridade, estável dentro da mesma prioridade) e
executa-os através do ``RuntimeManager``, recolhendo um relatório agregado
(``SchedulerReport``).

O scheduler distingue-se do gestor: o gestor executa um plano; o
scheduler decide **a ordem** e percorre os planos. Por omissão o
agendamento é **sequencial** e verificável.

Na unidade residual de concorrência entre planos (Fase 8), o scheduler
ganha o parâmetro aditivo ``concurrency``: com ``concurrency > 1`` os
planos são executados em paralelo (``ThreadPoolExecutor``), com
``concurrency == 1`` (padrão) o comportamento é exactamente o sequencial
histórico. O relatório preserva a ordem de prioridade em ambas as vias.

Na Fase 8.9 (Gate de addons), o scheduler passa a propagar o motor de
política (8.8) ao gestor: o contrato de composição estabelece que quem
cria o ``RuntimeManager``/``Scheduler`` fornece o ``PolicyEngine`` real,
sendo o scheduler o ponto de instituição junto da fila de agendamento.
As filas de espera multicamadas continuam posterior.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

from wsai2.core.context import ExecutionContext, ExecutionPriority
from wsai2.core.errors import ValidationError
from wsai2.security import PolicyEngine

from .base import ExecutionReport, ScheduleOutcome, SchedulerReport, StepRunner
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
        concurrency: int = 1,
        step_runner: StepRunner | None = None,
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
            concurrency: número máximo de planos executados em paralelo.
                Com ``1`` (padrão) o agendamento é sequencial e idêntico ao
                histórico. Com ``> 1`` os planos correm em threads de
                trabalho, por lotes de ``concurrency``; os contextos são
                materializados no thread principal, os ``execution_id`` têm
                de ser únicos no agendamento e o relatório preserva a
                ordem de prioridade.
            step_runner: executor de cada passo, propagado ao gestor
                (aditivo; sem runner, os passos são observados sem
                operação, como directamente no ``RuntimeManager``).

        Returns:
            O relatório do agendamento, com a ordem efectiva e os
            resultados por plano.

        Raises:
            ValidationError: se ``concurrency`` não for um inteiro >= 1 ou,
                em modo paralelo, dois planos partilharem ``execution_id``.
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

        ordem = sorted(plans, key=_chave)
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
        """Caminho histórico: executa os planos em sequência."""
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
        """Caminho paralelo (aditivo): executa os planos em threads.

        Os contextos são materializados **no thread principal** (execução
        única e ordem estável) e, sem ``context_factory``, os
        ``execution_id`` são derivados com um ordinal para garantir
        unicidade dentro do agendamento. Com ``stop_on_failure``, uma
        falha sinaliza os planos ainda não iniciados (que não executam);
        os que já decorrem concluem e são reportados.
        """
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