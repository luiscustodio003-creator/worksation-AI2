"""Runtime Engine — gestor de execução, scheduler e filas.

O scheduler mantém a via directa histórica por omissão. As filas
multicamadas são uma capacidade aditiva e opt-in, fornecendo prioridade,
backlog e preempção apenas de trabalho ainda pendente.
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
from .queue import MultilayerExecutionQueue, QueueItem, QueueSnapshot, priority_for_plan
from .scheduler import Scheduler

__all__ = [
    "ExecutionMonitor",
    "ExecutionReport",
    "ExecutionSnapshot",
    "ExecutionStatus",
    "MonitorSnapshot",
    "MultilayerExecutionQueue",
    "QueueItem",
    "QueueSnapshot",
    "QueueSnapshot",
    "RuntimeManager",
    "ScheduleOutcome",
    "Scheduler",
    "SchedulerReport",
    "StepOutcome",
    "StepRunner",
    "StepStatus",
    "priority_for_plan",
]
