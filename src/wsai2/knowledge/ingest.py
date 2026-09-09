"""Ingestão de ficheiros de texto do projecto (Fase 9.7).

Lê ficheiros de texto suportados sob um directório raiz e produz
``KnowledgeRecord`` (tipo ``document``) com proveniência pelo caminho
relativo e metadados derivados pelo extractor (9.3): idioma e etiquetas
heurísticos. A ingestão é **lexical** — não recorre a embeddings nem a
Model/Provider; o enriquecimento semântico (embeddings) fica para
decisão própria e está deliberadamente fora desta unidade.

Responsabilidade única: transformar ficheiros de texto do projecto em
registos do contrato 9.1, prontos a admitir no ``KnowledgeRegistry``
(9.2), persistir (9.5) e indexar (9.4/9.6).
"""

from __future__ import annotations

from pathlib import Path

from .base import KnowledgeKind, KnowledgeMetadata, KnowledgeRecord
from .metadata import KnowledgeMetadataExtractor

_EXTENSOES_TEXTUAIS = {
    ".md",
    ".py",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
}

_LIMITE_BYTES_POR_OMISSAO = 1_000_000


class FileIngestor:
    """Ingere ficheiros de texto do projecto em registos de conhecimento.

    Determinista (ordem por caminho relativo), sem estado e sem I/O além
    da leitura pedida. Ficheiros não textuais, vazios ou acima do limite
    de tamanho são ignorados sem falhar.
    """

    def __init__(self, extrator: KnowledgeMetadataExtractor | None = None) -> None:
        """Prepara o ingestor com o extractor de metadados (9.3)."""
        self._extrator = extrator or KnowledgeMetadataExtractor()

    def ingest(
        self,
        raiz: str | Path,
        *,
        limite_bytes: int = _LIMITE_BYTES_POR_OMISSAO,
    ) -> tuple[KnowledgeRecord, ...]:
        """Lê os ficheiros suportados sob ``raiz`` e devolve registos.

        Args:
            raiz: directório a percorrer recursivamente.
            limite_bytes: tamanho máximo de ficheiro a ingerir.

        Returns:
            Registos do contrato, ordenados pelo caminho relativo.
        """
        directoria = Path(raiz)
        ficheiros = sorted(
            (
                caminho
                for caminho in directoria.rglob("*")
                if caminho.is_file()
                and caminho.suffix in _EXTENSOES_TEXTUAIS
            ),
            key=lambda p: p.relative_to(directoria).as_posix(),
        )
        registos: list[KnowledgeRecord] = []
        for ficheiro in ficheiros:
            if ficheiro.stat().st_size > limite_bytes:
                continue
            texto = ficheiro.read_text(encoding="utf-8", errors="replace")
            if not texto.strip():
                continue
            registo = self._para_registo(ficheiro.relative_to(directoria), texto)
            registos.append(registo)
        return tuple(registos)

    def _para_registo(self, relativo: Path, conteudo: str) -> KnowledgeRecord:
        """Constrói o registo do contrato a partir de um ficheiro."""
        source = relativo.as_posix()
        base = KnowledgeRecord(
            id=f"km.f.{source}",
            title=relativo.name,
            content=conteudo,
            kind=KnowledgeKind.DOCUMENT,
            metadata=KnowledgeMetadata(source=source),
        )
        metadados = self._extrator.extract(base)
        return KnowledgeRecord(
            id=base.id,
            title=base.title,
            content=base.content,
            kind=base.kind,
            metadata=metadados,
        )


__all__ = ["FileIngestor"]