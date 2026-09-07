"""Subsistema Task Intelligence do WorkStation AI 2.

Responsável por definir e analisar o que o sistema tem de fazer —
tarefas, requisitos, capacidades e plano de execução (subsistema 3.7
da arquitectura).

Nesta unidade é implementada a **classificação de tarefas**: a
categoria de modelo mais adequada a cada tarefa, derivada
deterministicamente do seu tipo funcional. A classificação liga o
contrato de tarefa ao Model Intelligence. As unidades seguintes mapeiam
requisitos/capacidades e constroem o plano de execução.
"""

from .base import Task, TaskKind
from .classification import (
    TaskClassification,
    category_for_task,
    classify_task,
    classify_tasks,
)

__all__ = [
    "Task",
    "TaskClassification",
    "TaskKind",
    "category_for_task",
    "classify_task",
    "classify_tasks",
]