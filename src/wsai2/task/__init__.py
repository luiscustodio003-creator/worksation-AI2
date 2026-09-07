"""Subsistema Task Intelligence do WorkStation AI 2.

Responsável por definir e analisar o que o sistema tem de fazer —
tarefas, requisitos, capacidades e plano de execução (subsistema 3.7
da arquitectura).

Nesta unidade é implementada a **selecção de capacidades**: a
verificação, contra o Capability Engine, de quais capacidades exigidas
pela tarefa estão disponíveis, determinando a viabilidade da execução.
A unidade final constrói o plano de execução.
"""

from .base import Task, TaskKind
from .capability_selection import TaskCapabilitySelection, select_capabilities
from .classification import (
    TaskClassification,
    category_for_task,
    classify_task,
    classify_tasks,
)
from .requirements import (
    TaskRequirements,
    capabilities_for_task,
    requirements_for,
    requirements_for_many,
)

__all__ = [
    "Task",
    "TaskCapabilitySelection",
    "TaskClassification",
    "TaskKind",
    "TaskRequirements",
    "capabilities_for_task",
    "category_for_task",
    "classify_task",
    "classify_tasks",
    "requirements_for",
    "requirements_for_many",
    "select_capabilities",
]