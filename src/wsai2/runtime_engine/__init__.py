"""Runtime Engine — gestor de execução, scheduler e filas.

O scheduler mantém a via directa histórica por omissão. As filas
multicamadas são uma capacidade aditiva e opt-in, fornecendo prioridade,
backlog e preempção apenas de trabalho ainda pendente.

Desde o KERNEL-09, este pacote é **apenas a fronteira** (shell de
re-export): a superfície sancionada mantém-se aqui, mas a implementação
pesada (tipos, gestor, monitor, filas e scheduler) desceu para
`wsai2.infrastructure`, por trás deste contrato público.
"""

from wsai2.infrastructure.base_runtime import (
    ExecutionReport,
    ExecutionStatus,
    ScheduleOutcome,
    SchedulerReport,
    StepOutcome,
    StepRunner,
    StepStatus,
)
from wsai2.infrastructure.manager import RuntimeManager
from wsai2.infrastructure.monitoring import ExecutionMonitor, ExecutionSnapshot, MonitorSnapshot
from wsai2.infrastructure.queue import MultilayerExecutionQueue, QueueItem, QueueSnapshot, priority_for_plan
from wsai2.infrastructure.scheduler import Scheduler

# Contrato público da fronteira de governação (KERNEL-06): a superfície
# sancionada é o `__all__` abaixo, congelada por teste de contrato.
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