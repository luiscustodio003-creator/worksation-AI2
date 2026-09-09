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

# Contrato público da fronteira de governação (KERNEL-06): a superfície
# sancionada é o `__all__` abaixo, congelada por teste de contrato. A
# implementação pesada (colecção de métricas do monitor) permanece interna
# e desce para infra-estrutura no KERNEL-08/09.
RUNTIME_ENGINE_CONTRACT_VERSION = "1.0"

__all__ = [
    "ExecutionMonitor",
    "ExecutionReport",
    "ExecutionSnapshot",
    "ExecutionStatus",
    "MonitorSnapshot",
    "MultilayerExecutionQueue",
    "QueueItem",
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
