"""Subsistema de conhecimento do WorkStation AI 2.

Define o contrato declarativo (9.1), o registo central (9.2), a extracção
heurística de metadados (9.3) e o índice invertido em memória (9.4) do
Knowledge Engine (subsistema 3.9). Unidades posteriores da Fase 9 cuidam
da recuperação e da construção de contexto, com decisão própria antes de
qualquer persistência.
"""

from .base import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)
from .index import KnowledgeIndex
from .metadata import KnowledgeMetadataExtractor, derive_tags, detect_language, tokenize
from .registry import KnowledgeRegistry

__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "KnowledgeIndex",
    "KnowledgeKind",
    "KnowledgeMetadata",
    "KnowledgeMetadataExtractor",
    "KnowledgeRecord",
    "KnowledgeRegistry",
    "derive_tags",
    "detect_language",
    "tokenize",
]