"""Contratos do Runtime Engine (subsistema 3.8 — Fase 8.5).

Fecha o hardening 07 do CORE_HARDENING_PLAN: o gestor de execução e o
scheduler consomem o ``ExecutionPlan`` já produzido pelo Task
Intelligence (Fase 7) e aplicam sobre ele as políticas centralizadas da
Fase 8 (``execute_with_policies`` da 8.4 e ``ResourceGovernor`` da 8.3),
produzindo o **Execution Result** com observabilidade por passo.

Este módulo contém apenas tipos, estados e relatórios — a execução
concreta fica em ``manager.py`` (gestor de execução) e ``scheduler.py``
(agendamento determinístico por prioridade; sequencial por omissão, com
concorrência entre planos implementada como unidade residual aditiva via
``concurrency``). As filas de espera multicamadas permanecem posteriores,
fora do âmbito de 8.5.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Callable

from wsai2.core.public import ExecutionPriority, WsaiError

if TYPE_CHECKING:
    from wsai2.task import ExecutionPlan

StepRunner = Callable[[int, str], object]
"""Executor de um passo do plano: recebe o índice e a descrição do passo.

Sem runner fornecido, o ``RuntimeManager`` regista o passo sem operação
real; o operador do runtime fornece um runner que efectivamente realiza o
passo (ex.: invocação do modelo via fornecedor).
"""


class StepStatus(Enum):
    """Estado de um passo da execução de um plano."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStatus(Enum):
    """Estado global de uma execução de plano."""

    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class StepOutcome:
    """Resultado de um passo — a unidade de monitorização da 8.5.

    Attributes:
        index: posição do passo no plano.
        step: descrição do passo (do ``ExecutionPlan.steps``).
        status: estado do passo.
        duration: duração observada do passo (relógio injectável).
        error: erro que fez o passo falhar, quando aplicável.
    """

    index: int
    step: str
    status: StepStatus
    duration: float
    error: WsaiError | None = None

    @property
    def passed(self) -> bool:
        """Indica se o passo foi concluído com sucesso."""
        return self.status is StepStatus.SUCCESS


@dataclass(frozen=True)
class ExecutionReport:
    """Execution Result de um plano (hardening 07).

    Reúne o veredicto global da execução, os passos observados (incluindo
    os ``SKIPPED`` após a primeira falha) e o erro final, quando existir.

    Attributes:
        execution_id: identificador da execução (do contexto).
        task_id: identificador da tarefa (do plano).
        status: estado global da execução.
        steps: resultados por passo, na ordem do plano.
        duration: duração total observada da execução.
        error: erro que marcou a execução, quando aplicável.
    """

    execution_id: str
    task_id: str
    status: ExecutionStatus
    steps: tuple[StepOutcome, ...]
    duration: float
    error: WsaiError | None = None

    @property
    def is_success(self) -> bool:
        """Indica se a execução concluiu com sucesso."""
        return self.status is ExecutionStatus.SUCCESS

    @property
    def summary(self) -> str:
        """Resumo textual da execução para apresentação."""
        marca = "ok" if self.is_success else self.status.value
        return (
            f"{self.task_id}: {marca} "
            f"({self.duration:.3f}s, {_contagens(self.steps)})"
        )


@dataclass(frozen=True)
class ScheduleOutcome:
    """Resultado de um plano agendado pelo ``Scheduler``.

    Attributes:
        task_id: identificador da tarefa.
        priority: prioridade aplicada no agendamento.
        report: relatório de execução do plano.
    """

    task_id: str
    priority: ExecutionPriority
    report: ExecutionReport


@dataclass(frozen=True)
class SchedulerReport:
    """Relatório agregado do agendamento.

    Attributes:
        outcomes: resultados dos planos efectivamente executados, na
            ordem de execução decidida pelo scheduler.
        order: ordem de execução dos planos (por task_id).
        duration: duração total observada do agendamento.
    """

    outcomes: tuple[ScheduleOutcome, ...]
    order: tuple[str, ...]
    duration: float

    @property
    def total(self) -> int:
        """Número de planos executados."""
        return len(self.outcomes)

    @property
    def succeeded(self) -> int:
        """Número de planos concluídos com sucesso."""
        return sum(1 for outcome in self.outcomes if outcome.report.is_success)

    @property
    def failed(self) -> int:
        """Número de planos não concluídos (falha, timeout ou cancelamento)."""
        return self.total - self.succeeded

    @property
    def summary(self) -> str:
        """Resumo textual do agendamento para apresentação."""
        return (
            f"scheduler: {self.total} planos, {self.succeeded} ok, "
            f"{self.failed} falhados ({self.duration:.3f}s)"
        )


def _contagens(steps: tuple[StepOutcome, ...]) -> str:
    """Resumo das contagens por estado para os relatórios."""
    ok = sum(1 for passo in steps if passo.passed)
    falhados = sum(1 for passo in steps if passo.status is StepStatus.FAILED)
    restantes = len(steps) - ok - falhados
    partes = [f"{ok} ok"]
    if falhados:
        partes.append(f"{falhados} falhados")
    if restantes:
        partes.append(f"{restantes} não executados")
    return ", ".join(partes)


__all__ = [
    "ExecutionReport",
    "ExecutionStatus",
    "ScheduleOutcome",
    "SchedulerReport",
    "StepOutcome",
    "StepRunner",
    "StepStatus",
]