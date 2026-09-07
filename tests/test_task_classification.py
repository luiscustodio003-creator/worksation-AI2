"""Testes da classificação de tarefas do Task Intelligence.

Valida o mapeamento determinístico entre o tipo funcional da tarefa e a
categoria de modelo mais adequada.
"""

from wsai2.model.base import ModelCategory
from wsai2.task import (
    Task,
    TaskClassification,
    TaskKind,
    category_for_task,
    classify_task,
    classify_tasks,
)


def _tarefa(kind: TaskKind, id: str = "t") -> Task:
    return Task(id=id, kind=kind, prompt="texto")


def test_categoria_para_chat() -> None:
    """Uma tarefa de chat deve mapear para a categoria de chat."""
    assert category_for_task(_tarefa(TaskKind.CHAT)) is ModelCategory.CHAT


def test_categoria_para_completion() -> None:
    """Uma tarefa de completion deve mapear para a categoria de completion."""
    assert (
        category_for_task(_tarefa(TaskKind.COMPLETION))
        is ModelCategory.COMPLETION
    )


def test_categoria_para_embedding() -> None:
    """Uma tarefa de embedding deve mapear para a categoria de embedding."""
    assert (
        category_for_task(_tarefa(TaskKind.EMBEDDING))
        is ModelCategory.EMBEDDING
    )


def test_classificar_tarefa_devolve_classificacao() -> None:
    """A classificação deve conter id, tipo funcional e categoria."""
    classificacao = classify_task(_tarefa(TaskKind.CHAT, id="t-x"))

    assert isinstance(classificacao, TaskClassification)
    assert classificacao.task_id == "t-x"
    assert classificacao.kind is TaskKind.CHAT
    assert classificacao.category is ModelCategory.CHAT
    assert "t-x" in classificacao.summary


def test_classificar_tarefa_usa_tipo_funcional_como_fonte() -> None:
    """O tipo funcional é a fonte da verdade, mesmo com capacidades."""
    tarefa = Task(
        id="t-e",
        kind=TaskKind.EMBEDDING,
        prompt="Vectoriza",
        required_capabilities=("local_embeddings",),
    )

    assert classify_task(tarefa).category is ModelCategory.EMBEDDING


def test_classificar_tarefas_preserva_ordem() -> None:
    """A classificação de um conjunto deve preservar a ordem de entrada."""
    tarefas = (
        _tarefa(TaskKind.CHAT, id="a"),
        _tarefa(TaskKind.EMBEDDING, id="b"),
        _tarefa(TaskKind.COMPLETION, id="c"),
    )

    classificacoes = classify_tasks(tarefas)

    assert [c.task_id for c in classificacoes] == ["a", "b", "c"]
    assert [c.category for c in classificacoes] == [
        ModelCategory.CHAT,
        ModelCategory.EMBEDDING,
        ModelCategory.COMPLETION,
    ]


def test_classificar_tarefas_vazio() -> None:
    """Um conjunto vazio de tarefas deve devolver uma tupla vazia."""
    assert classify_tasks(()) == ()