"""Subsistema de conhecimento do WorkStation AI 2.

Define o contrato declarativo do Knowledge Engine (subsistema 3.9) na
unidade 9.1: o tipo de conhecimento, os metadados estruturados e o
registo de conhecimento imutável. Unidades posteriores da Fase 9
acrescentam ingestão, extracção, indexação, recuperação e construção de
contexto.
"""

from .base import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)

__all__ = [
    "KNOWLEDGE_CONTRACT_VERSION",
    "KnowledgeKind",
    "KnowledgeMetadata",
    "KnowledgeRecord",
]