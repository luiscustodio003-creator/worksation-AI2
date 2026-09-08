"""Subsistema de conhecimento do WorkStation AI 2.

Define o contrato declarativo (9.1), o registo central (9.2) e a
extracção heurística de metadados (9.3) do Knowledge Engine (subsistema
3.9). Unidades posteriores da Fase 9 acrescentam indexação, recuperação
e construção de contexto.
"""

from .base import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)
from .metadata import KnowledgeMetadataExtractor, derive_tags, detect_language
from .registry import KnowledgeRegistry

__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "KnowledgeKind",
    "KnowledgeMetadata",
    "KnowledgeMetadataExtractor",
    "KnowledgeRecord",
    "KnowledgeRegistry",
    "derive_tags",
    "detect_language",
]