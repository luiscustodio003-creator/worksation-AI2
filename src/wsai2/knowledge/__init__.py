"""Subsistema de conhecimento do WorkStation AI 2.

Define o contrato declarativo (9.1), o registo central (9.2), a extracção
heurística de metadados (9.3), o índice invertido em memória (9.4), a
persistência SQLite (9.5) e a construção de contexto (9.6) do Knowledge
Engine (subsistema 3.9).
"""

from .base import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)
from .context import ContextBuilder, ContextEntry, KnowledgeContext
from .index import KnowledgeIndex
from .metadata import KnowledgeMetadataExtractor, derive_tags, detect_language, tokenize
from .registry import KnowledgeRegistry
from .storage import KnowledgeStore

__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "ContextBuilder",
    "ContextEntry",
    "KnowledgeContext",
    "KnowledgeIndex",
    "KnowledgeKind",
    "KnowledgeMetadata",
    "KnowledgeMetadataExtractor",
    "KnowledgeRecord",
    "KnowledgeRegistry",
    "KnowledgeStore",
    "derive_tags",
    "detect_language",
    "tokenize",
]