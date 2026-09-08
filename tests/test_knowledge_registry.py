"""Testes do registo de conhecimento (Fase 9.2).

Valida o padrão de catálogo (admissão, consultas, remoção, ordem) e a
barreira de unicidade de ``id`` — rejeição antes de o registo ser
admitido. O registo não ingere, extrai, indexa nem pesquisa.
"""

import pytest

from wsai2.core.errors import ValidationError
from wsai2.knowledge import (
    KnowledgeKind,
    KnowledgeRecord,
    KnowledgeRegistry,
)


def _registo(
    identifier: str = "km.documento.01",
    *,
    title: str = "Documento de exemplo",
    content: str = "Conteúdo textual de exemplo.",
    kind: KnowledgeKind = KnowledgeKind.DOCUMENT,
) -> KnowledgeRecord:
    """Constrói um registo de conhecimento de teste pronto para admissão."""
    return KnowledgeRecord(
        id=identifier,
        title=title,
        content=content,
        kind=kind,
    )


def test_registar_admite_e_preserva_identidade() -> None:
    """O registo deve admitir um registo e preservá-lo por id."""
    registo = KnowledgeRegistry()
    admitido = registo.register(_registo("km.a"))
    assert admitido.id == "km.a"
    assert registo.get("km.a") is admitido
    assert registo.has("km.a")


def test_registar_devolve_o_mesmo_objeto() -> None:
    """O ``register`` deve devolver o objecto admitido, sem cópia."""
    registo = KnowledgeRegistry()
    registo_declarado = _registo("km.original")
    admitido = registo.register(registo_declarado)
    assert admitido is registo_declarado


def test_registar_rejeita_id_duplicado() -> None:
    """Um id admitido uma segunda vez deve ser rejeitado sem corromper."""
    registo = KnowledgeRegistry()
    registo.register(_registo("km.a"))
    with pytest.raises(ValidationError) as erro:
        registo.register(_registo("km.a"))
    assert erro.value.code == "wsai.knowledge.duplicate"
    assert len(registo) == 1
    assert registo.has("km.a")


def test_versao_suportada_por_defeito() -> None:
    """A versão suportada deve ser a constante da base por omissão."""
    assert KnowledgeRegistry().supported_contract_version == "1.0"


def test_consultas_sobre_o_catalogo() -> None:
    """get/has/all/len devem reflectir fielmente o catálogo."""
    registo = KnowledgeRegistry()
    assert not registo.has("km.a")
    assert registo.get("km.a") is None
    registo.register(_registo("km.a"))
    registo.register(_registo("km.b", title="Segundo documento"))
    assert registo.has("km.a")
    assert registo.get("km.b").id == "km.b"  # type: ignore[union-attr]
    assert len(registo) == 2
    assert [r.id for r in registo.all()] == ["km.a", "km.b"]


def test_ordem_de_admissao_preservada() -> None:
    """O catálogo deve devolver os registos por ordem de admissão."""
    registo = KnowledgeRegistry()
    registo.register(_registo("km.1"))
    registo.register(_registo("km.2"))
    registo.register(_registo("km.3"))
    assert [r.id for r in registo.all()] == ["km.1", "km.2", "km.3"]


def test_unregister_remove_do_catalogo() -> None:
    """Unregister deve remover e devolver True apenas quando existia."""
    registo = KnowledgeRegistry()
    registo.register(_registo("km.a"))
    assert registo.unregister("km.a")
    assert not registo.has("km.a")
    assert not registo.unregister("km.a")
    assert len(registo) == 0


def test_registo_aceita_tipos_distintos() -> None:
    """O catálogo deve aceitar registos de tipos distintos."""
    registo = KnowledgeRegistry()
    registo.register(_registo("km.doc", kind=KnowledgeKind.DOCUMENT))
    registo.register(_registo("km.note", kind=KnowledgeKind.NOTE))
    assert registo.get("km.doc").kind is KnowledgeKind.DOCUMENT  # type: ignore[union-attr]
    assert registo.get("km.note").kind is KnowledgeKind.NOTE  # type: ignore[union-attr]