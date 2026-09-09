"""Subsistema de conhecimento do WorkStation AI 2.

Define o contrato declarativo (9.1), o registo central (9.2), a extracção
heurística de metadados (9.3), o índice invertido em memória (9.4), a
persistência SQLite (9.5), a construção de contexto (9.6) e a ingestão de
ficheiros de texto do projecto (9.7) do Knowledge Engine (subsistema
3.9). O enriquecimento semântico via embeddings fica para decisão própria
posterior.
"""

from .base import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)
from .context import ContextBuilder, ContextEntry, KnowledgeContext
from .index import KnowledgeIndex
from .ingest import FileIngestor
from .metadata import KnowledgeMetadataExtractor, derive_tags, detect_language, tokenize
from .registry import KnowledgeRegistry
from .storage import KnowledgeStore

__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "ContextBuilder",
    "ContextEntry",
    "FileIngestor",
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