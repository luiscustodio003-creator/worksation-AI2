"""Subsistema Task Intelligence do WorkStation AI 2.

Responsável por definir e analisar o que o sistema tem de fazer —
tarefas, requisitos, capacidades e plano de execução (subsistema 3.7
da arquitectura).

Nesta unidade final é implementado o **plano de execução**: a
integração dos requisitos, da viabilidade, da recomendação de modelo e
de um fornecedor saudável num plano determinístico, encerrando a Fase 7.
"""

from .base import Task, TaskKind
from .capability_selection import TaskCapabilitySelection, select_capabilities
from .classification import (
    TaskClassification,
    category_for_task,
    classify_task,
    classify_tasks,
)
from .plan import ExecutionPlan, build_execution_plan
from .requirements import (
    TaskRequirements,
    capabilities_for_task,
    requirements_for,
    requirements_for_many,
)

__all__ = [
    "ExecutionPlan",
    "Task",
    "TaskCapabilitySelection",
    "TaskClassification",
    "TaskKind",
    "TaskRequirements",
    "build_execution_plan",
    "capabilities_for_task",
    "category_for_task",
    "classify_task",
    "classify_tasks",
    "requirements_for",
    "requirements_for_many",
    "select_capabilities",
]