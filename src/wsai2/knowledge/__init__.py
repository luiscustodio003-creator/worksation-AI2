"""Subsistema de conhecimento do WorkStation AI 2.

Define o contrato declarativo (9.1) e o registo central (9.2) do
Knowledge Engine (subsistema 3.9): o tipo de conhecimento, os metadados
estruturados, o registo de conhecimento imutável e a admissão por id
único. Unidades posteriores da Fase 9 acrescentam ingestão, extracção,
indexação, recuperação e construção de contexto.
"""

from .base import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)
from .registry import KnowledgeRegistry

__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "KnowledgeKind",
    "KnowledgeMetadata",
    "KnowledgeRecord",
    "KnowledgeRegistry",
]