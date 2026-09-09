"""Testes da ingestão de ficheiros de texto (Fase 9.7).

Valida a transformação de ficheiros em registos do contrato (tipo
``document``, proveniência relativa, metadados derivados), a selecção de
extensões, a ordem determinista e a integração com registo/índice/
contexto — sem embeddings e sem I/O fora dos exemplos de teste.
"""

from pathlib import Path

from wsai2.knowledge import (
    ContextBuilder,
    FileIngestor,
    KnowledgeIndex,
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRegistry,
)


def _criar_projeto(tmp_path: Path) -> Path:
    """Constrói um mini projecto de texto para ingestão."""
    raiz = tmp_path / "projeto"
    (raiz / "docs").mkdir(parents=True)
    (raiz / "src").mkdir()
    (raiz / "docs" / "guia.md").write_text(
        "Este documento descreve as regras e a arquitectura do sistema.", encoding="utf-8"
    )
    (raiz / "src" / "modulo.py").write_text(
        "def funcao():\n    return 'conteudo funcional'\n", encoding="utf-8"
    )
    (raiz / "ignorado.bin").write_bytes(b"\x00\x01\x02")
    (raiz / "docs" / "vazio.txt").write_text("   \n", encoding="utf-8")
    return raiz


def test_ingest_cria_registos_do_contrato(tmp_path) -> None:
    """A ingestão deve produzir registos document do contrato 9.1."""
    raiz = _criar_projeto(tmp_path)
    registos = FileIngestor().ingest(raiz)
    assert len(registos) == 2
    for registo in registos:
        assert registo.kind is KnowledgeKind.DOCUMENT
        assert registo.metadata.source.startswith("docs/") or registo.metadata.source.startswith("src/")


def test_ordem_determinista_por_caminho(tmp_path) -> None:
    """Os registos devem vir ordenados pelo caminho relativo e repetíveis."""
    raiz = _criar_projeto(tmp_path)
    ingestor = FileIngestor()
    primeiro = ingestor.ingest(raiz)
    segundo = ingestor.ingest(raiz)
    sources = [r.metadata.source for r in primeiro]
    assert sources == sorted(sources)
    assert sources == [r.metadata.source for r in segundo]
    assert primeiro == segundo


def test_id_pela_proveniencia_relativa(tmp_path) -> None:
    """O id deve derivar do caminho relativo do ficheiro."""
    raiz = _criar_projeto(tmp_path)
    registos = FileIngestor().ingest(raiz)
    for registo in registos:
        assert registo.id == f"km.f.{registo.metadata.source}"


def test_titulo_e_idioma_derivados(tmp_path) -> None:
    """Título e idioma devem ser derivados do ficheiro e do conteúdo."""
    raiz = _criar_projeto(tmp_path)
    registos = FileIngestor().ingest(raiz)
    guia = next(r for r in registos if r.metadata.source == "docs/guia.md")
    assert guia.title == "guia.md"
    assert guia.metadata.language == "pt-PT"
    assert guia.metadata.tags


def test_extensoes_nao_suportadas_e_vazios_ignorados(tmp_path) -> None:
    """Ficheiros binários e vazios não devem ser ingeridos."""
    raiz = _criar_projeto(tmp_path)
    registos = FileIngestor().ingest(raiz)
    assert all(r.metadata.source != "ignorado.bin" for r in registos)
    assert not any(r.id.endswith("vazio.txt") for r in registos)


def test_limite_de_tamanho_ignora_ficheiros_grandes(tmp_path) -> None:
    """Ficheiros acima do limite devem ser omitidos."""
    raiz = tmp_path / "grades"
    raiz.mkdir()
    (raiz / "grande.md").write_text("a" * 10_000, encoding="utf-8")
    (raiz / "pequeno.md").write_text("texto pequeno", encoding="utf-8")
    registos = FileIngestor().ingest(raiz, limite_bytes=1_000)
    assert [r.metadata.source for r in registos] == ["pequeno.md"]


def test_ingest_directoria_vazia(tmp_path) -> None:
    """Um directório vazio deve devolver tuplo vazio."""
    raiz = tmp_path / "vazio"
    raiz.mkdir()
    assert FileIngestor().ingest(raiz) == ()


def test_integracao_com_registo_indice_e_contexto(tmp_path) -> None:
    """Ingerir→admitir→indexar→consultar deve devolver contexto útil."""
    raiz = tmp_path / "projeto"
    raiz.mkdir()
    (raiz / "nota.md").write_text(
        "Este apontamento guarda a decisão de arquitectura do sistema.",
        encoding="utf-8",
    )

    registo = KnowledgeRegistry()
    for record in FileIngestor().ingest(raiz):
        registo.register(record)

    indice = KnowledgeIndex()
    indice.build(registo)

    contexto = ContextBuilder().build("arquitectura", indice, top=1)
    assert len(contexto.entries) == 1
    assert contexto.entries[0].record_id == "km.f.nota.md"
    assert contexto.entries[0].source == "nota.md"
    assert "decisão de arquitectura" in contexto.entries[0].snippet


def test_metadados_sao_instancia_do_contrato(tmp_path) -> None:
    """Os metadados gerados devem respeitar o tipo do contrato."""
    raiz = _criar_projeto(tmp_path)
    registo = FileIngestor().ingest(raiz)[0]
    assert isinstance(registo.metadata, KnowledgeMetadata)