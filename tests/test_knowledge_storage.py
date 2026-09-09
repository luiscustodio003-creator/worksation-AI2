"""Testes da persistência SQLite de conhecimento (Fase 9.5).

Valida o ciclo de guardar/carregar do contrato 9.1 (por id, com
metadados serializados), a substituição pelo id, a remoção, a contagem e
a recuperação integrada com o registo e o índice em memória.
"""

import sqlite3

from wsai2.knowledge import (
    KnowledgeIndex,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
    KnowledgeRegistry,
    KnowledgeStore,
)


def _registo(
    identifier: str,
    *,
    title: str = "Documento de exemplo",
    content: str = "Conteúdo de exemplo.",
    tags: tuple[str, ...] = (),
    extras: dict[str, str] | None = None,
) -> KnowledgeRecord:
    """Constrói um registo válido para persistência."""
    return KnowledgeRecord(
        id=identifier,
        title=title,
        content=content,
        kind=KnowledgeKind.DOCUMENT,
        metadata=KnowledgeMetadata(
            source="docs/exemplo.md",
            language="pt-PT",
            author="og.quim",
            tags=tags,
            extras=extras or {},
        ),
        created_at="2026-09-09T00:00:00",
    )


def test_ciclo_completo_de_persistencia(tmp_path) -> None:
    """Guardar e carregar deve reconstruir o registo integralmente."""
    caminho = tmp_path / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    esperado = _registo("km.ciclo", tags=("regra",), extras={"revisao": "2"})
    marca.save(esperado)
    carregados = marca.load()
    assert len(carregados) == 1
    carregado = carregados[0]
    assert carregado.id == esperado.id
    assert carregado.title == esperado.title
    assert carregado.content == esperado.content
    assert carregado.kind is esperado.kind
    assert carregado.metadata.tags == ("regra",)
    assert carregado.metadata.extras == {"revisao": "2"}
    assert carregado.metadata.language == "pt-PT"
    assert carregado.metadata.author == "og.quim"
    assert carregado.created_at == esperado.created_at


def test_substituicao_pelo_id(tmp_path) -> None:
    """Guardar sobre o mesmo id deve substituir, sem duplicar."""
    caminho = tmp_path / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    marca.save(_registo("km.a", content="primeiro"))
    marca.save(_registo("km.a", content="segundo"))
    carregados = marca.load()
    assert len(carregados) == 1
    assert carregados[0].content == "segundo"


def test_delete_devolve_estado(tmp_path) -> None:
    """delete deve devolver True apenas se o registo existia."""
    caminho = tmp_path / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    marca.save(_registo("km.a"))
    assert marca.delete("km.a")
    assert not marca.delete("km.a")
    assert marca.count() == 0


def test_contagem_e_carga_no_armazenamento_vazio(tmp_path) -> None:
    """Um armazenamento recém-criado deve começar vazio."""
    caminho = tmp_path / "novo.db"
    marca = KnowledgeStore(caminho)
    assert marca.count() == 0
    assert marca.load() == ()


def test_ficheiro_e_esquema_criados(tmp_path) -> None:
    """O ficheiro SQLite e a tabela devem existir após a criação."""
    caminho = tmp_path / "sub" / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    assert caminho.is_file()
    with sqlite3.connect(caminho) as con:
        tabela = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='knowledge_record'"
        ).fetchone()
    assert tabela is not None
    assert marca.path == caminho


def test_ordem_de_carga_determinista(tmp_path) -> None:
    """A carga deve respeitar a ordem alfabética do id."""
    caminho = tmp_path / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    marca.save_all((_registo("km.z"), _registo("km.a"), _registo("km.m")))
    assert [r.id for r in marca.load()] == ["km.a", "km.m", "km.z"]


def test_caracteres_acentuados_preservados(tmp_path) -> None:
    """Etiquetas e extras com acentos devem sobreviver ao ciclo."""
    caminho = tmp_path / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    marca.save(_registo("km.a", tags=("construção",), extras={"idioma": "português"}))
    carregado = marca.load()[0]
    assert carregado.metadata.tags == ("construção",)
    assert carregado.metadata.extras["idioma"] == "português"


def test_recuperacao_integrada_com_registo_e_indice(tmp_path) -> None:
    """Persistir→carregar→admitir→indexar→consultar deve funcionar."""
    caminho = tmp_path / "conhecimento.db"
    marca = KnowledgeStore(caminho)
    marca.save(_registo("km.a", content="termo pesquisável"))
    marca.save(_registo("km.b", content="outro conteúdo"))

    registo = KnowledgeRegistry()
    for record in marca.load():
        registo.register(record)

    indice = KnowledgeIndex()
    indice.build(registo)
    resultado = indice.search("pesquisável")
    assert resultado[0][0].id == "km.a"