"""Testes do contrato de tarefa do Task Intelligence.

Valida a representação do pedido de trabalho: tipo funcional, texto,
máximo de tokens, capacidades exigidas e metadados opacos.
"""

import pytest

from wsai2.task import Task, TaskKind


def test_criar_tarefa_com_valores_por_defeito() -> None:
    """Uma tarefa simples deve usar os valores por defeito."""
    tarefa = Task(id="t-1", kind=TaskKind.CHAT, prompt="Olá")

    assert tarefa.id == "t-1"
    assert tarefa.kind is TaskKind.CHAT
    assert tarefa.prompt == "Olá"
    assert tarefa.max_tokens == 256
    assert tarefa.required_capabilities == ()
    assert tarefa.metadata == {}


def test_tarefa_imutavel() -> None:
    """A tarefa deve ser imutável (frozen dataclass)."""
    tarefa = Task(id="t-1", kind=TaskKind.CHAT, prompt="Olá")

    with pytest.raises(Exception):
        tarefa.prompt = "outro texto"  # type: ignore[misc]


def test_tipos_funcionais_da_tarefa() -> None:
    """Devem existir os tipos funcionais chat, completion e embedding."""
    assert TaskKind.CHAT.value == "chat"
    assert TaskKind.COMPLETION.value == "completion"
    assert TaskKind.EMBEDDING.value == "embedding"


def test_tarefa_com_capacidades_requeridas() -> None:
    """As capacidades exigidas devem ser preservadas na ordem e conteúdo."""
    tarefa = Task(
        id="t-2",
        kind=TaskKind.EMBEDDING,
        prompt="Vectoriza este texto",
        required_capabilities=("local_embeddings",),
    )

    assert tarefa.required_capabilities == ("local_embeddings",)


def test_tarefa_com_metadados_opacos() -> None:
    """Os metadados devem suportar contexto extra sem interpretar."""
    tarefa = Task(
        id="t-3",
        kind=TaskKind.CHAT,
        prompt="Resume",
        metadata={"conversation_id": "abc-123"},
    )

    assert tarefa.metadata == {"conversation_id": "abc-123"}


def test_tarefa_max_tokens_personalizado() -> None:
    """O máximo de tokens deve ser configurável por tarefa."""
    tarefa = Task(
        id="t-4",
        kind=TaskKind.COMPLETION,
        prompt="Continua a história",
        max_tokens=128,
    )

    assert tarefa.max_tokens == 128


def test_tarefa_prompt_vazio_invalido() -> None:
    """Uma tarefa sem texto deve ser rejeitada."""
    with pytest.raises(ValueError):
        Task(id="t-invalida", kind=TaskKind.CHAT, prompt="")


def test_tarefa_max_tokens_invalido() -> None:
    """Um máximo de tokens não positivo deve ser rejeitado."""
    with pytest.raises(ValueError):
        Task(id="t-invalida", kind=TaskKind.CHAT, prompt="Olá", max_tokens=0)


def test_tarefa_sumario() -> None:
    """O resumo deve conter o tipo funcional e o id."""
    tarefa = Task(id="t-5", kind=TaskKind.CHAT, prompt="Olá")

    assert "chat" in tarefa.summary
    assert "t-5" in tarefa.summary