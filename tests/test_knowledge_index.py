"""Testes do índice invertido em memória (Fase 9.4).

Valida a indexação por termos com pesos de campo, a normalização
partilhada, a reindexação por substituição, a remoção e a ordenação
determinista — sem I/O, persistência ou embeddings.
"""

from wsai2.knowledge import (
    KnowledgeIndex,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
    KnowledgeRegistry,
)


def _registo(
    identifier: str,
    *,
    title: str = "Título de exemplo",
    content: str = "Conteúdo de exemplo do registo.",
    tags: tuple[str, ...] = (),
) -> KnowledgeRecord:
    """Constrói um registo válido para indexação."""
    return KnowledgeRecord(
        id=identifier,
        title=title,
        content=content,
        kind=KnowledgeKind.DOCUMENT,
        metadata=KnowledgeMetadata(tags=tags),
    )


def test_indexar_e_consultar_por_termo() -> None:
    """Um registo indexado deve ser encontrado por um termo do conteúdo."""
    indice = KnowledgeIndex()
    registo = _registo("km.a", content="O sistema guarda conhecimento fiável.")
    indice.index(registo)
    resultado = indice.search("sistema")
    assert [(r.id, pontuacao) for r, pontuacao in resultado] == [("km.a", 1)]


def test_consultas_sem_resultado() -> None:
    """Uma consulta sem correspondências deve devolver tuplo vazio."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.a"))
    assert indice.search("inexistente") == ()
    assert indice.search("") == ()


def test_normalizacao_partilhada_de_consulta() -> None:
    """A consulta deve ser normalizada como o conteúdo (casefold)."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.a", content="Registo Supremo Fiável"))
    assert indice.search("supremo")[0][0].id == "km.a"
    assert indice.search("SUPREMO")[0][0].id == "km.a"


def test_peso_do_titulo_sobre_o_conteudo() -> None:
    """Uma correspondência no título deve pontuar acima de uma no conteúdo."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.t", title="empacotador rápido", content="outros termos"))
    indice.index(_registo("km.c", title="outro título", content="empacotador lento"))
    resultado = indice.search("empacotador")
    ids = [r.id for r, _ in resultado]
    assert ids[:2] == ["km.t", "km.c"]


def test_peso_das_etiquetas() -> None:
    """Uma correspondência nas etiquetas deve somar o peso de etiqueta."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.1", content="contexto decorado", tags=("lexicografia",)))
    indice.index(_registo("km.2", content="lexicografia contextos variados"))
    resultado = indice.search("lexicografia")
    ids = [r.id for r, _ in resultado]
    pontuacoes = {r.id: p for r, p in resultado}
    assert ids[:2] == ["km.1", "km.2"]
    assert pontuacoes["km.1"] == 2
    assert pontuacoes["km.2"] == 1


def test_reindexar_substitui_conteudo() -> None:
    """Indexar de novo a mesma identidade deve substituir sem acumular."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.a", content="termo exclusivo"))
    indice.index(_registo("km.a", content="termo renovado"))
    assert indice.search("exclusivo") == ()
    assert indice.search("renovado")[0][0].id == "km.a"
    assert len(indice) == 1


def test_unindex_remove_as_entradas() -> None:
    """Remover um registo deve apagar as suas entradas do índice."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.a", content="termo especial"))
    assert indice.unindex("km.a")
    assert indice.search("especial") == ()
    assert len(indice) == 0
    assert not indice.unindex("km.a")


def test_build_indexa_do_registo() -> None:
    """O ``build`` deve indexar todos os registos admitidos."""
    registo = KnowledgeRegistry()
    registo.register(_registo("km.a", content="conteúdo partilhado"))
    registo.register(_registo("km.b", content="conteúdo outro"))
    indice = KnowledgeIndex()
    indice.build(registo)
    assert indice.search("partilhado")[0][0].id == "km.a"
    assert [r.id for r, _ in indice.search("conteúdo")] == ["km.a", "km.b"]


def test_ordenacao_determinista_por_id() -> None:
    """Empates de pontuação devem ser desfeitos pela ordem do id."""
    indice = KnowledgeIndex()
    indice.index(_registo("km.z", content="termo comum"))
    indice.index(_registo("km.a", content="termo comum"))
    resultado = indice.search("termo")
    assert [r.id for r, _ in resultado] == ["km.a", "km.z"]


def test_limite_dos_resultados() -> None:
    """A consulta deve respeitar o limite pedido."""
    indice = KnowledgeIndex()
    for numero in range(5):
        indice.index(_registo(f"km.{numero}", content="termo colectivo"))
    resultado = indice.search("termo", limit=3)
    assert len(resultado) == 3
    assert [r.id for r, _ in indice.search("termo")] == [
        f"km.{n}" for n in range(5)
    ]


def test_indexar_vazio_e_indice_vazio() -> None:
    """Índice sem registos deve ter tamanho zero e sem resultado."""
    indice = KnowledgeIndex()
    assert len(indice) == 0
    assert indice.search("qualquer") == ()