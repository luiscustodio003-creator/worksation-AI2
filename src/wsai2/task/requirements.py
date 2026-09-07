"""Requisitos de uma tarefa.

Materializa as exigências de uma tarefa num contrato de requisitos
consumível pelo Model Intelligence: a **categoria de modelo** (derivada
da classificação) e as **capacidades** que o sistema tem de disponibilizar.

As capacidades vêm da própria tarefa, deduplicadas por ordem; nada é
inventado para a tarefa (auditoria BASE-19: o catálogo não inventa
métricas nem capacidades).
"""

from __future__ import annotations

from dataclasses import dataclass

from wsai2.model.base import ModelCategory

from .base import Task
from .classification import category_for_task


def capabilities_for_task(task: Task) -> tuple[str, ...]:
    """Devolve as capacidades exigidas pela tarefa, únicas e por ordem.

    Preserva a ordem de declaração e remove duplicados, sem inventar
    capacidades para a tarefa.
    """
    return tuple(dict.fromkeys(task.required_capabilities))


@dataclass(frozen=True)
class TaskRequirements:
    """Requisitos de execução de uma tarefa.

    Reúne a categoria de modelo adequada, as capacidades exigidas
    (únicas, por ordem) e o máximo de tokens de resposta.
    """

    task_id: str
    category: ModelCategory
    required_capabilities: tuple[str, ...]
    max_tokens: int

    @property
    def summary(self) -> str:
        """Resumo textual dos requisitos para apresentação."""
        return f"{self.task_id} ({self.category.value}, {self.max_tokens} tokens)"


def requirements_for(task: Task) -> TaskRequirements:
    """Constrói os requisitos de execução de uma tarefa."""
    return TaskRequirements(
        task_id=task.id,
        category=category_for_task(task),
        required_capabilities=capabilities_for_task(task),
        max_tokens=task.max_tokens,
    )


def requirements_for_many(
    tasks: tuple[Task, ...],
) -> tuple[TaskRequirements, ...]:
    """Constrói os requisitos de um conjunto de tarefas, por ordem."""
    return tuple(requirements_for(task) for task in tasks)


__all__ = [
    "TaskRequirements",
    "capabilities_for_task",
    "requirements_for",
    "requirements_for_many",
]