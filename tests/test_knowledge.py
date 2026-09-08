"""Testes do contrato do Knowledge Engine (Fase 9.1).

Valida o contrato declarativo do subsistema 3.9: construção, validação
à criação, imutabilidade, defaults, enums (tipos de conhecimento) e
resumo textual.
"""

import pytest

from wsai2.knowledge import (
    KNOWLEDGE_CONTRACT_VERSION,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)


def _registo(
    *,
    identifier: str = "km.documento.01",
    title: str = "Documento de exemplo",
    content: str = "Conteúdo textual de exemplo.",
    kind: KnowledgeKind = KnowledgeKind.DOCUMENT,
    metadata: KnowledgeMetadata | None = None,
    created_at: str = "",
) -> KnowledgeRecord:
    """Constrói um registo de conhecimento de teste."""
    return KnowledgeRecord(
        id=identifier,
        title=title,
        content=content,
        kind=kind,
        metadata=metadata or KnowledgeMetadata(),
        created_at=created_at,
    )


def test_registo_valido_com_todos_os_campos() -> None:
    """Um registo completo deve construir sem erros e preservar os valores."""
    metadados = KnowledgeMetadata(
        source="pipelines/relatorio.md",
        language="pt",
        author="wsai",
        tags=("manual", "v1"),
        extras={"revisao": "3"},
    )
    registo = _registo(
        identifier="km.extract.02",
        title="Resumo da revisão",
        content="Extracto sintetizado.",
        kind=KnowledgeKind.EXTRACT,
        metadata=metadados,
        created_at="2026-09-09T10:00:00Z",
    )

    assert registo.id == "km.extract.02"
    assert registo.title == "Resumo da revisão"
    assert registo.content == "Extracto sintetizado."
    assert registo.kind is KnowledgeKind.EXTRACT
    assert registo.metadata is metadados
    assert registo.metadata.source == "pipelines/relatorio.md"
    assert registo.metadata.tags == ("manual", "v1")
    assert registo.created_at == "2026-09-09T10:00:00Z"


def test_registo_defaults_aplicados() -> None:
    """Os campos opcionais devem ter os valores predefinidos documentados."""
    registo = _registo()

    assert registo.metadata.source == ""
    assert registo.metadata.language == ""
    assert registo.metadata.author == ""
    assert registo.metadata.tags == ()
    assert registo.metadata.extras == {}
    assert registo.created_at == ""


def test_registo_imutavel() -> None:
    """Um registo validado não deve ser modificável (frozen)."""
    registo = _registo()
    with pytest.raises(Exception):
        registo.title = "Título alterado"  # type: ignore[misc]


def test_registo_rejeita_id_vazio() -> None:
    """Um id vazio deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _registo(identifier="")


def test_registo_rejeita_titulo_vazio() -> None:
    """Um título vazio deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _registo(title="")


def test_registo_rejeita_conteudo_vazio() -> None:
    """Um conteúdo vazio deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _registo(content="")


def test_registo_rejeita_tipo_ausente() -> None:
    """Um tipo (kind) ausente ou nulo deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _registo(kind=None)  # type: ignore[arg-type]


def test_enum_tipos_cobre_categorias_previstas() -> None:
    """O tipo de conhecimento deve cobrir as categorias previstas."""
    valores = {kind.value for kind in KnowledgeKind}
    assert {"document", "extract", "note"} <= valores


def test_versao_de_contrato_definida() -> None:
    """A versão suportada do contrato deve estar declarada."""
    assert KNOWLEDGE_CONTRACT_VERSION == "1.0"


def test_registo_resumo_textual() -> None:
    """O registo deve expor um resumo textual com título e tipo."""
    registo = _registo(
        title="Nota operacional",
        kind=KnowledgeKind.NOTE,
    )
    resumo = registo.summary
    assert "Nota operacional" in resumo
    assert "note" in resumo