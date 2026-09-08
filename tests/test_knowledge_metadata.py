"""Testes da extracção heurística de metadados (Fase 9.3).

Valida a detecção de idioma, a derivação de etiquetas, a preservação da
proveniência e o determinismo — sem I/O, sem modelos e sem estado.
"""

import pytest

from wsai2.knowledge import (
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeMetadataExtractor,
    KnowledgeRecord,
    derive_tags,
    detect_language,
)

_TEXTO_PT = (
    "Este documento descreve as regras e a arquitectura do sistema "
    "para garantir a construção fiável do conhecimento."
)
_TEXTO_EN = (
    "The system architecture and the rules are described in this "
    "document for future reference and reuse across projects."
)


def _registo(*, content: str, metadata: KnowledgeMetadata | None = None) -> KnowledgeRecord:
    """Constrói um registo válido pronto para extracção."""
    return KnowledgeRecord(
        id="km.extract.01",
        title="Documento de teste",
        content=content,
        kind=KnowledgeKind.DOCUMENT,
        metadata=metadata or KnowledgeMetadata(),
    )


def test_detectar_idioma_portugues() -> None:
    """Conteúdo em português deve ser detectado como pt-PT."""
    assert detect_language(_TEXTO_PT) == "pt-PT"


def test_detectar_idioma_ingles() -> None:
    """Conteúdo em inglês deve ser detectado como en."""
    assert detect_language(_TEXTO_EN) == "en"


def test_detectar_idioma_empate_devolve_indeterminado() -> None:
    """Sem decisão confiável (empate) deve devolver "und"."""
    assert detect_language("the and e de que") == "und"
    assert detect_language("") == "und"


def test_extrair_preenche_idioma_em_falta() -> None:
    """A extracção deve completar o idioma quando não está declarado."""
    metadados = KnowledgeMetadataExtractor().extract(_registo(content=_TEXTO_PT))
    assert metadados.language == "pt-PT"


def test_extrair_preserva_idioma_explicito() -> None:
    """O idioma explícito não deve ser sobreposto pela heurística."""
    metadados = KnowledgeMetadataExtractor().extract(
        _registo(content=_TEXTO_EN, metadata=KnowledgeMetadata(language="fr"))
    )
    assert metadados.language == "fr"


def test_derivar_etiquetas_exclui_palavras_de_ligacao() -> None:
    """As palavras de ligação não devem constar das etiquetas."""
    etiquetas = derive_tags("o sistema regista documentos de teste")
    assert etiquetas[:3] == ("documentos", "regista", "sistema")
    assert "o" not in etiquetas and "de" not in etiquetas


def test_derivar_etiquetas_por_frequencia() -> None:
    """Os termos mais frequentes devem surgir primeiro."""
    etiquetas = derive_tags("python python python e java java")
    assert etiquetas[:1] == ("python",)
    assert "java" in etiquetas


def test_derivar_etiquetas_respeita_limite() -> None:
    """O número de etiquetas derivadas deve respeitar o limite."""
    assert len(derive_tags(_TEXTO_PT, limit=2)) <= 2
    assert len(derive_tags("sem conteúdo relevante", limit=0)) == 0


def test_extrair_preserva_proveniencia() -> None:
    """source, author e extras declarados devem sobreviver à extracção."""
    metadados = KnowledgeMetadataExtractor().extract(
        _registo(
            content=_TEXTO_PT,
            metadata=KnowledgeMetadata(
                source="docs/project/PROJECT_STATE.md",
                author="og.quim",
                tags=("estado",),
                extras={"revisao": "3"},
            ),
        )
    )
    assert metadados.source == "docs/project/PROJECT_STATE.md"
    assert metadados.author == "og.quim"
    assert metadados.extras == {"revisao": "3"}


def test_extrair_une_etiquetas_explicitas_e_derivadas() -> None:
    """As etiquetas explícitas devem anteceder as derivadas, sem duplicar."""
    metadados = KnowledgeMetadataExtractor().extract(
        _registo(
            content=_TEXTO_PT,
            metadata=KnowledgeMetadata(tags=("regras",)),
        )
    )
    assert metadados.tags[0] == "regras"
    assert metadados.tags.count("regras") == 1
    assert len(metadados.tags) >= 3


def test_extrair_foi_determinista() -> None:
    """Duas extracções do mesmo registo devem ser idênticas."""
    extractor = KnowledgeMetadataExtractor()
    reg = _registo(content=_TEXTO_PT)
    assert extractor.extract(reg) == extractor.extract(reg)


def test_extrair_com_metadados_por_omissao() -> None:
    """Registo sem metadados declarados deve ser totalmente derivado."""
    resultante = KnowledgeMetadataExtractor().extract(_registo(content=_TEXTO_PT))
    assert resultante.language == "pt-PT"
    assert resultante.source == ""
    assert resultante.tags


def test_codigos_de_idioma_suportados_nao_vazios_em_palavra_unica() -> None:
    """Marcadores sem texto longo não devem rebentar com tokens de 3 letras."""
    assert detect_language("the") == "en"
    assert detect_language("de") == "pt-PT"


def test_extractor_rejeita_conteudo_invalido() -> None:
    """O extractor não deve aceitar registos contra o contrato."""
    with pytest.raises(ValueError):
        _registo(content="")