"""Testes dos requisitos de tarefa do Task Intelligence.

Valida a materialização das exigências de uma tarefa: categoria,
capacidades (únicas e por ordem) e máximo de tokens.
"""

from wsai2.model.base import ModelCategory
from wsai2.task import (
    Task,
    TaskKind,
    TaskRequirements,
    capabilities_for_task,
    requirements_for,
    requirements_for_many,
)


def test_capacidades_preservam_ordem() -> None:
    """As capacidades devem manter a ordem de declaração."""
    tarefa = Task(
        id="t-1",
        kind=TaskKind.CHAT,
        prompt="Olá",
        required_capabilities=("acc-b", "acc-a"),
    )

    assert capabilities_for_task(tarefa) == ("acc-b", "acc-a")


def test_capacidades_deduplicam() -> None:
    """Capacidades repetidas devem aparecer uma única vez."""
    tarefa = Task(
        id="t-2",
        kind=TaskKind.CHAT,
        prompt="Olá",
        required_capabilities=("a", "b", "a"),
    )

    assert capabilities_for_task(tarefa) == ("a", "b")


def test_capacidades_vazias() -> None:
    """Uma tarefa sem capacidades deve devolver uma tupla vazia."""
    tarefa = Task(id="t-3", kind=TaskKind.CHAT, prompt="Olá")
    assert capabilities_for_task(tarefa) == ()


def test_requisitos_devolvem_contrato() -> None:
    """Os requisitos devem conter categoria, capacidades e tokens."""
    tarefa = Task(
        id="t-4",
        kind=TaskKind.EMBEDDING,
        prompt="Vectoriza",
        max_tokens=512,
        required_capabilities=("local_embeddings", "local_embeddings"),
    )

    requisitos = requirements_for(tarefa)

    assert isinstance(requisitos, TaskRequirements)
    assert requisitos.task_id == "t-4"
    assert requisitos.category is ModelCategory.EMBEDDING
    assert requisitos.required_capabilities == ("local_embeddings",)
    assert requisitos.max_tokens == 512
    assert "t-4" in requisitos.summary


def test_requisitos_categoria_derivada() -> None:
    """A categoria deve ser derivada do tipo funcional da tarefa."""
    requisitos = requirements_for(
        Task(id="t-5", kind=TaskKind.COMPLETION, prompt="Continua")
    )

    assert requisitos.category is ModelCategory.COMPLETION
    assert requisitos.required_capabilities == ()


def test_requisitos_preservam_max_tokens_por_defeito() -> None:
    """Sem max_tokens explícito, deve ser usado o valor por defeito."""
    requisitos = requirements_for(Task(id="t-6", kind=TaskKind.CHAT, prompt="Olá"))

    assert requisitos.max_tokens == 256


def test_requisitos_para_muitas_tarefas() -> None:
    """Os requisitos de um conjunto devem preservar a ordem."""
    tarefas = (
        Task(id="a", kind=TaskKind.CHAT, prompt="p"),
        Task(id="b", kind=TaskKind.EMBEDDING, prompt="q"),
    )

    requisitos = requirements_for_many(tarefas)

    assert [requisito.task_id for requisito in requisitos] == ["a", "b"]
    assert [requisito.category for requisito in requisitos] == [
        ModelCategory.CHAT,
        ModelCategory.EMBEDDING,
    ]


def test_requisitos_vazio() -> None:
    """Um conjunto vazio de tarefas deve devolver uma tupla vazia."""
    assert requirements_for_many(()) == ()