"""Contratos e tipos fundamentais do Task Intelligence.

Define o **contrato de tarefa** e a sua representação — o pedido de
trabalho que o sistema vai analisar e executar. Independe do fornecedor
e do modelo (constituição, artigo 13): a tarefa apenas declara o tipo
funcional, o texto e as capacidades que exige.

As unidades seguintes da Fase 7 classificam tarefas, mapeiam
capacidades e constroem o plano de execução.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TaskKind(Enum):
    """Tipo funcional da tarefa, alinhado com as categorias de modelo."""

    CHAT = "chat"              # Diálogo e instruções
    COMPLETION = "completion"  # Geração de texto livre
    EMBEDDING = "embedding"    # Representações vectoriais


@dataclass(frozen=True)
class Task:
    """Representação imutável de uma tarefa.

    A tarefa é o pedido de trabalho: um texto (ou contexto), um tipo
    funcional e as capacidades do sistema que a sua execução exige.
    Não contém referência a fornecedores ou modelos — essa decisão é
    tomada em unidades posteriores.
    """

    id: str
    kind: TaskKind
    prompt: str
    max_tokens: int = 256
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida a representação da tarefa no momento da criação."""
        if not self.prompt:
            raise ValueError("a tarefa precisa de um texto (prompt) não vazio")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens deve ser positivo")

    @property
    def summary(self) -> str:
        """Resumo textual da tarefa para apresentação."""
        return f"{self.kind.value}: {self.id}"


__all__ = ["Task", "TaskKind"]