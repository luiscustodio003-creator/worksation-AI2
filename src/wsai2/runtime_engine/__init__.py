"""Runtime Engine — gestor de execução e scheduler (subsistema 3.8).

Unidade 8.5 do hardening controlado da Fase 8 (hardening 07 do
CORE_HARDENING_PLAN): executa o ``ExecutionPlan`` produzido pelo Task
Intelligence (Fase 7), aplicando as políticas centralizadas de timeout,
cancelamento e recuperação (8.4) e a governação de recursos (8.3), e
agenda múltiplos planos por prioridade de forma determinística.

Fora de âmbito desta unidade: lifecycle de extensões (8.6 — subsistema
``wsai2.extension``) e filas com concorrência entre planos. A observabilidade
cobre execução (``ExecutionReport``), agendamento (``SchedulerReport``) e,
desde a unidade residual de monitorização contínua, o estado **em curso** via
``ExecutionMonitor`` (``snapshot()`` interroga as execuções enquanto decorrem,
de outra thread, sem esperar pelo relatório final).
"""

from .base import (
    ExecutionReport,
    ExecutionStatus,
    ScheduleOutcome,
    SchedulerReport,
    StepOutcome,
    StepRunner,
    StepStatus,
)
from .manager import RuntimeManager
from .monitoring import ExecutionMonitor, ExecutionSnapshot, MonitorSnapshot
from .scheduler import Scheduler

__all__ = [
    "ExecutionMonitor",
    "ExecutionReport",
    "ExecutionSnapshot",
    "ExecutionStatus",
    "MonitorSnapshot",
    "RuntimeManager",
    "ScheduleOutcome",
    "Scheduler",
    "SchedulerReport",
    "StepOutcome",
    "StepRunner",
    "StepStatus",
]