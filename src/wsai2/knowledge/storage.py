"""Persistência SQLite do conhecimento (Fase 9.5).

Decisão documentada (2026-09-09 — ver `PROJECT_STATE.md`, unidade 9.5 e
`docs/knowledge/BASE-41-knowledge-sqlite-persistence.md`): a estratégia de
armazenamento adoptada para a recuperação é **SQLite local** (stdlib
``sqlite3``), transversal a Windows/Linux. Os registos do contrato 9.1 são
persistidos por ``id`` e recuperáveis para reconstruir o
``KnowledgeRegistry`` e o ``KnowledgeIndex``.

Responsabilidade única desta unidade: guardar/carregar ``KnowledgeRecord``
de um ficheiro SQLite. Não pesquisa nem indexa por si — a consulta é do
índice em memória (9.4), alimentado pelos registos carregados daqui.
"""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from .base import KnowledgeKind, KnowledgeMetadata, KnowledgeRecord

_TABELA = "knowledge_record"

_COLUNAS = (
    "id",
    "title",
    "content",
    "kind",
    "metadata_source",
    "metadata_language",
    "metadata_author",
    "metadata_tags",
    "metadata_extras",
    "created_at",
)

_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {_TABELA} (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    kind TEXT NOT NULL,
    metadata_source TEXT NOT NULL DEFAULT '',
    metadata_language TEXT NOT NULL DEFAULT '',
    metadata_author TEXT NOT NULL DEFAULT '',
    metadata_tags TEXT NOT NULL DEFAULT '[]',
    metadata_extras TEXT NOT NULL DEFAULT '{{}}',
    created_at TEXT NOT NULL DEFAULT ''
);
"""


class KnowledgeStore:
    """Armazenamento SQLite local dos registos de conhecimento.

    Persiste registos do contrato 9.1 por ``id`` (chave primária), com os
    metadados serializados em JSON. Cada operação abre e fecha a ligação,
    mantendo o armazenamento simples e sem estado em memória para além do
    caminho do ficheiro.
    """

    def __init__(self, path: str | Path) -> None:
        """Cria (ou reutiliza) o ficheiro SQLite no caminho dado.

        O directório pai é criado se não existir e o esquema é aplicado.
        """
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._ligacao() as con:
            con.execute(_SCHEMA)

    @property
    def path(self) -> Path:
        """Caminho do ficheiro SQLite."""
        return self._path

    @contextmanager
    def _ligacao(self):
        con = sqlite3.connect(self._path)
        try:
            with con:
                yield con
        finally:
            con.close()

    def save(self, registo: KnowledgeRecord) -> None:
        """Guarda um registo, substituindo qualquer registo com o mesmo id."""
        colunas = ",".join(_COLUNAS)
        marcadores = ",".join("?" for _ in _COLUNAS)
        actualiza = ",".join(
            f"{coluna}=excluded.{coluna}" for coluna in _COLUNAS[1:]
        )
        with self._ligacao() as con:
            con.execute(
                f"INSERT INTO {_TABELA} ({colunas}) VALUES ({marcadores}) "
                f"ON CONFLICT(id) DO UPDATE SET {actualiza}",
                self._linha(registo),
            )

    def save_all(self, registos: tuple[KnowledgeRecord, ...] | list[KnowledgeRecord]) -> None:
        """Guarda vários registos numa transacção."""
        for registo in registos:
            self.save(registo)

    def delete(self, record_id: str) -> bool:
        """Apaga um registo pelo id.

        Devolve ``True`` se o registo existia e foi apagado.
        """
        with self._ligacao() as con:
            cursor = con.execute(
                f"DELETE FROM {_TABELA} WHERE id = ?", (record_id,)
            )
            return cursor.rowcount > 0

    def count(self) -> int:
        """Número de registos persistidos."""
        with self._ligacao() as con:
            return con.execute(f"SELECT COUNT(*) FROM {_TABELA}").fetchone()[0]

    def load(self) -> tuple[KnowledgeRecord, ...]:
        """Carrega todos os registos, ordenados pelo id.

        Devolve os registos tal como foram persistidos, reconstruindo
        tipos e metadados do contrato 9.1.
        """
        colunas = ",".join(_COLUNAS)
        with self._ligacao() as con:
            linhas = con.execute(
                f"SELECT {colunas} FROM {_TABELA} ORDER BY id"
            ).fetchall()
        return tuple(self._para_registo(linha) for linha in linhas)

    def _linha(self, registo: KnowledgeRecord) -> tuple:
        """Serializa um registo no formato das colunas da tabela."""
        metadata = registo.metadata
        return (
            registo.id,
            registo.title,
            registo.content,
            registo.kind.value,
            metadata.source,
            metadata.language,
            metadata.author,
            json.dumps(list(metadata.tags), ensure_ascii=False),
            json.dumps(metadata.extras, ensure_ascii=False),
            registo.created_at,
        )

    @staticmethod
    def _para_registo(linha: tuple) -> KnowledgeRecord:
        """Reconstrói um registo do contrato a partir de uma linha SQL."""
        (
            registro_id,
            title,
            content,
            kind,
            origem,
            idioma,
            autor,
            etiquetas,
            extras,
            data_criacao,
        ) = linha
        return KnowledgeRecord(
            id=registro_id,
            title=title,
            content=content,
            kind=KnowledgeKind(kind),
            metadata=KnowledgeMetadata(
                source=origem,
                language=idioma,
                author=autor,
                tags=tuple(json.loads(etiquetas)),
                extras=dict(json.loads(extras)),
            ),
            created_at=data_criacao,
        )


__all__ = ["KnowledgeStore"]