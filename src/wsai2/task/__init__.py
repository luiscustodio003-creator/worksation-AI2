"""Subsistema Task Intelligence do WorkStation AI 2.

Responsável por definir e analisar o que o sistema tem de fazer —
tarefas, requisitos, capacidades e plano de execução (subsistema 3.7
da arquitectura).

Nesta unidade são implementados os **requisitos de tarefa**: a
materialização das exigências de uma tarefa (categoria de modelo e
capacidades únicas) num contrato consumível pelo Model Intelligence.
As unidades seguintes seleccionam capacidades e constroem o plano de
execução.
"""

from .base import Task, TaskKind
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
    "TaskClassification",
    "TaskKind",
    "TaskRequirements",
    "capabilities_for_task",
    "category_for_task",
    "classify_task",
    "classify_tasks",
    "requirements_for",
    "requirements_for_many",
]