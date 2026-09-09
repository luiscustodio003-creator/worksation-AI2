"""Testes da construção de contexto (Fase 9.6).

Valida a montagem determinista de contexto a partir do índice em memória:
entradas por relevância, excertos truncados, metadados preservados e
texto serializado estável — sem I/O e sem modelos.
"""

from wsai2.knowledge import (
    ContextBuilder,
    KnowledgeContext,
    KnowledgeIndex,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
)


def _indice_com(
    conteudos: dict[str, tuple[str, str]],
    *,
    tags: dict[str, tuple[str, ...]] | None = None,
) -> KnowledgeIndex:
    """Constrói um índice com registos definidos por id→(título, conteúdo)."""
    indice = KnowledgeIndex()
    for registro_id, (titulo, conteudo) in conteudos.items():
        indice.index(
            KnowledgeRecord(
                id=registro_id,
                title=titulo,
                content=conteudo,
                kind=KnowledgeKind.DOCUMENT,
                metadata=KnowledgeMetadata(
                    source=f"docs/{registro_id}.md",
                    tags=(tags or {}).get(registro_id, ()),
                ),
            )
        )
    return indice


def test_construir_contexto_por_relevancia() -> None:
    """As entradas devem seguir a ordem de relevância do índice."""
    indice = _indice_com(
        {
            "km.a": ("Relevante", "documento relevante para a consulta"),
            "km.b": ("Marginal", "texto completamente irrelevante aqui"),
        }
    )
    contexto = ContextBuilder().build("relevante", indice)
    assert isinstance(contexto, KnowledgeContext)
    assert [e.record_id for e in contexto.entries] == ["km.a"]


def test_entradas_transportam_metadados() -> None:
    """Título, fonte e etiquetas devem acompanhar a entrada."""
    indice = _indice_com(
        {"km.a": ("Política", "política de segurança documentada")},
        tags={"km.a": ("segurança", "regra")},
    )
    entrada = ContextBuilder().build("política", indice).entries[0]
    assert entrada.title == "Política"
    assert entrada.source == "docs/km.a.md"
    assert entrada.tags == ("segurança", "regra")


def test_excerto_truncado_com_elipse() -> None:
    """Conteúdos longos devem ser truncados com elipse final."""
    indice = _indice_com({"km.a": ("T", "palavra " * 100)})
    contexto = ContextBuilder().build("palavra", indice, snippet_caracteres=20)
    excerto = contexto.entries[0].snippet
    assert excerto.endswith("…")
    assert len(excerto) <= 20 + 1


def test_excerto_curto_mantem_integro() -> None:
    """Conteúdos curtos não devem ser truncados nem ganhar elipse."""
    indice = _indice_com({"km.a": ("T", "texto curto")})
    entrada = ContextBuilder().build("texto", indice).entries[0]
    assert entrada.snippet == "texto curto"


def test_sem_resultados_contexto_vazio() -> None:
    """Consulta sem correspondências deve produzir contexto vazio."""
    indice = _indice_com({"km.a": ("T", "conteúdo qualquer")})
    contexto = ContextBuilder().build("não-encontrado", indice)
    assert contexto.entries == ()
    assert contexto.query == "não-encontrado"


def test_limite_de_entradas() -> None:
    """O contexto deve respeitar o top pedido."""
    indice = _indice_com(
        {f"km.{n}": ("T", "termo comum") for n in range(6)}
    )
    contexto = ContextBuilder().build("termo", indice, top=3)
    assert len(contexto.entries) == 3


def test_texto_serializado_determinista() -> None:
    """A representação textual deve incluir consulta, título e ser estável."""
    indice = _indice_com({"km.a": ("Documento A", "conteúdo de teste")})
    contexto = ContextBuilder().build("teste", indice)
    texto = contexto.text()
    assert "CONSULTA: teste" in texto
    assert "[km.a] Documento A" in texto
    assert "conteúdo de teste" in texto
    assert texto == ContextBuilder().build("teste", indice).text()


def test_pontuacao_influencia_posicao_das_entradas() -> None:
    """O título pontua mais: registo de título exacto deve liderar."""
    conteudos = {
        "km.a": ("termo comum", "outro conteúdo qualquer"),
        "km.b": ("outro título", "o termo comum aparece no corpo"),
    }
    indice = _indice_com(conteudos)
    contexto = ContextBuilder().build("termo comum", indice)
    assert [e.record_id for e in contexto.entries] == ["km.a", "km.b"]