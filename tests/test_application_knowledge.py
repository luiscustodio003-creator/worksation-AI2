"""Testes do use-case Knowledge Context (APP-09).

Verifica que ``KnowledgeContextService`` indexa o registo fornecido,
pesquisa a consulta (com filtro opcional por tipo) e constrói o contexto —
sem decidir armazenamento nem política semântica.
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2 import knowledge as _knowledge
from wsai2.application import (
    KnowledgeContextRequest,
    KnowledgeContextResponse,
    KnowledgeContextService,
)


def _registo_com_contexto() -> _knowledge.KnowledgeRegistry:
    registo = _knowledge.KnowledgeRegistry()
    registo.register(
        _knowledge.KnowledgeRecord(
            id="km.a",
            title="Registo Supremo",
            content="arquitectura modular do WorkStation",
            kind=_knowledge.KnowledgeKind.DOCUMENT,
        )
    )
    registo.register(
        _knowledge.KnowledgeRecord(
            id="km.b",
            title="Nota de política",
            content="política de segurança por defeito",
            kind=_knowledge.KnowledgeKind.NOTE,
        )
    )
    return registo


def test_resolve_devolve_correspondencias_e_contexto() -> None:
    """APP-09: por omissão, o serviço pesquisa no registo e constrói contexto."""
    servico = KnowledgeContextService(registry_source=_registo_com_contexto)
    resposta = servico.resolve(KnowledgeContextRequest(query="arquitectura"))
    assert isinstance(resposta, KnowledgeContextResponse)
    assert resposta.query == "arquitectura"
    assert {registo.id for registo in resposta.matches} == {"km.a"}
    assert resposta.context is not None
    assert resposta.context.query == "arquitectura"


def test_resolve_filtra_por_tipo_de_conhecimento() -> None:
    """APP-09: o filtro por tipo restringe as correspondências."""
    servico = KnowledgeContextService(registry_source=_registo_com_contexto)
    resposta = servico.resolve(
        KnowledgeContextRequest(
            query="política", kind=_knowledge.KnowledgeKind.NOTE
        )
    )
    assert {registo.id for registo in resposta.matches} == {"km.b"}


def test_resolve_sem_resultados_devolve_contexto_vazio() -> None:
    """APP-09: sem correspondências, o contexto é vazio mas válido."""
    servico = KnowledgeContextService(registry_source=_registo_com_contexto)
    resposta = servico.resolve(KnowledgeContextRequest(query="inexistente-termo"))
    assert resposta.matches == ()
    assert resposta.context.entries == ()


def test_resolve_registo_vazio_e_imutavel() -> None:
    """APP-09: registo vazio e resposta imutável respeitam o contrato."""
    servico = KnowledgeContextService()
    resposta = servico.resolve(KnowledgeContextRequest(query="termo"))
    assert resposta.matches == ()
    with pytest.raises(FrozenInstanceError):
        resposta.query = "outra"