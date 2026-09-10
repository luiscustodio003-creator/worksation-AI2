"""Serviço do use-case de conhecimento (APP-09).

Monta o ``KnowledgeContextResponse`` a partir de ``wsai2.knowledge``:
indexa o registo fornecido, pesquisa a consulta (com filtro opcional por
tipo de conhecimento) e constrói o contexto — a Application não decide
a localização do armazenamento nem a política semântica.
"""

from __future__ import annotations

from typing import Callable

from wsai2 import knowledge as _knowledge

from .contract import KnowledgeContextRequest, KnowledgeContextResponse

RegistrySource = Callable[[], _knowledge.KnowledgeRegistry]


class KnowledgeContextService:
    """Resolve o use-case de contexto de conhecimento (APP-09).

    Attributes:
        registry_source: fonte do registo de registos de conhecimento.
    """

    def __init__(self, registry_source: RegistrySource | None = None) -> None:
        self._registry_source = (
            registry_source if registry_source is not None else _knowledge.KnowledgeRegistry
        )

    def resolve(self, request: KnowledgeContextRequest) -> KnowledgeContextResponse:
        """Devolve as correspondências e o contexto da consulta."""
        registo = self._registry_source()
        indice = _knowledge.KnowledgeIndex()
        indice.build(registo)

        resultados = indice.search(request.query, limit=request.limit)
        matches = tuple(registo for registo, _ in resultados)
        if request.kind is not None:
            matches = tuple(
                registo
                for registo in matches
                if registo.kind is request.kind
            )

        contexto = _knowledge.ContextBuilder().build(
            request.query, indice, top=request.limit
        )
        return KnowledgeContextResponse(
            query=request.query,
            matches=matches,
            context=contexto,
        )