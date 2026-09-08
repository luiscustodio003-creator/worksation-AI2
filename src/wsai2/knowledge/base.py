"""Contratos e tipos fundamentais do Knowledge Engine.

Este módulo contém apenas definições de tipos e dataclasses — não
implementa ingestão, extracção, metadados dinâmicos, indexação,
recuperação nem construção de contexto. Define o contrato mínimo comum
do subsistema 3.9 (Fase 9 — Knowledge Engine): a classificação do
conhecimento, os metadados estruturados e o registo de conhecimento
imutável que as unidades posteriores da Fase 9 irão consumir.

O contrato é declarativo e imutável; serve de base para a ingestão, a
extracção, a indexação e a recuperação sem acoplar esta unidade a
modelos, fornecedores ou armazenamento. As fontes são referidas por
identificador textual (source), de modo reversível e sem criar
dependência prematura com o Provider Layer ou com qualquer motor de
embeddings (constituição, artigo 8 — crescimento controlado).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

KNOWLEDGE_CONTRACT_VERSION = "1.0"


class KnowledgeKind(Enum):
    """Tipo funcional de uma unidade de conhecimento.

    Estas categorias não são uma lista fechada; representam a origem
    provável do conhecimento gerido pelo subsistema. Servem de base às
    unidades de ingestão/extracção e à construção de contexto da Fase 9.
    """

    DOCUMENT = "document"  # Fonte/documento ingerido
    EXTRACT = "extract"    # Conhecimento extraído/derivado de fonte(s)
    NOTE = "note"          # Conhecimento declarado manualmente


@dataclass(frozen=True)
class KnowledgeMetadata:
    """Metadados estruturados de uma unidade de conhecimento.

    Declara a proveniência, o idioma, o autor e as etiquetas de um
    conhecimento de forma imutável. A exploração e a extracção
    automática de metadados pertencem a unidades posteriores da Fase 9;
    aqui apenas se declara o contrato.
    """

    source: str = ""
    language: str = ""
    author: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    extras: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeRecord:
    """Registo declarativo de uma unidade de conhecimento.

    Define a identidade, o título, o conteúdo, o tipo e os metadados de
    um conhecimento. É imutável e validado à criação. Contém apenas
    dados — nenhuma lógica de ingestão, indexação ou pesquisa.
    """

    id: str
    title: str
    content: str
    kind: KnowledgeKind
    metadata: KnowledgeMetadata = field(default_factory=KnowledgeMetadata)
    created_at: str = ""

    def __post_init__(self) -> None:
        """Valida o registo no momento da criação."""
        if not self.id:
            raise ValueError("o conhecimento precisa de um id não vazio")
        if not self.title:
            raise ValueError("o conhecimento precisa de um título não vazio")
        if not self.content:
            raise ValueError("o conhecimento precisa de conteúdo não vazio")
        if self.kind is None:
            raise ValueError("o conhecimento precisa de um tipo (kind) válido")

    @property
    def summary(self) -> str:
        """Resumo textual do conhecimento para apresentação."""
        return f"{self.title} ({self.kind.value})"


__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "KnowledgeKind",
    "KnowledgeMetadata",
    "KnowledgeRecord",
]