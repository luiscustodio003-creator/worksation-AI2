"""Classificação de tarefas por categoria funcional de modelo.

Determina, de forma determinística, a **categoria de modelo** mais
adequada a cada tarefa, a partir do seu tipo funcional. O resultado
liga o Task Intelligence ao Model Intelligence (que decide o modelo) —
respeitando a separação do artigo 13: a tarefa decide a categoria; o
Model Intelligence decide o modelo; o Provider Layer decide o
fornecedor.
"""

from __future__ import annotations

from dataclasses import dataclass

from wsai2.model.base import ModelCategory

from .base import Task, TaskKind

# Mapa determinístico entre o tipo funcional da tarefa e a categoria de
# modelo correspondente. Alinhado com a semântica do TaskKind.
_CATEGORY_BY_KIND: dict[TaskKind, ModelCategory] = {
    TaskKind.CHAT: ModelCategory.CHAT,
    TaskKind.COMPLETION: ModelCategory.COMPLETION,
    TaskKind.EMBEDDING: ModelCategory.EMBEDDING,
}


@dataclass(frozen=True)
class TaskClassification:
    """Classificação de uma tarefa: tipo funcional e categoria de modelo."""

    task_id: str
    kind: TaskKind
    category: ModelCategory

    @property
    def summary(self) -> str:
        """Resumo textual da classificação para apresentação."""
        return f"{self.task_id} → {self.category.value}"


def category_for_task(task: Task) -> ModelCategory:
    """Devolve a categoria de modelo adequada ao tipo da tarefa.

    O tipo funcional é a fonte da verdade; a categoria é derivada do
    mapa determinístico ``_CATEGORY_BY_KIND``.
    """
    return _CATEGORY_BY_KIND[task.kind]


def classify_task(task: Task) -> TaskClassification:
    """Classifica uma tarefa quanto à categoria de modelo adequada."""
    return TaskClassification(
        task_id=task.id,
        kind=task.kind,
        category=category_for_task(task),
    )


def classify_tasks(tasks: tuple[Task, ...]) -> tuple[TaskClassification, ...]:
    """Classifica um conjunto de tarefas, preservando a ordem."""
    return tuple(classify_task(task) for task in tasks)


__all__ = [
    "TaskClassification",
    "category_for_task",
    "classify_task",
    "classify_tasks",
]