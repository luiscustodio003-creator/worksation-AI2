"""Construção de contexto de conhecimento (Fase 9.6).

Monta, a partir da consulta ao índice em memória (9.4) e dos registos
persistidos (9.5), um pacote de contexto textual **determinista**: as
entradas mais relevantes com título, excerto, proveniência e etiquetas,
prontas a servir de contexto a um modelo. Esta unidade não invoca
modelos nem faz I/O — apenas serializa texto.

Responsabilidade única desta unidade: produzir ``KnowledgeContext`` a
partir de um índice. O encaixe final com Model/Provider (fornecimento do
contexto a um modelo) fica para a integração, com decisões próprias.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import KnowledgeRecord
from .index import KnowledgeIndex

_ELLIPSIS = "…"


@dataclass(frozen=True)
class ContextEntry:
    """Uma entrada de contexto resultante da recuperação.

    Transporta os elementos deterministas que um consumidor (modelo,
    sumarizador...) pode usar sem aceder ao registo original.
    """

    record_id: str
    title: str
    snippet: str
    source: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgeContext:
    """Pacote de contexto montado para uma consulta.

    ``entries`` preserva a ordem de relevância do índice. ``text()``
    gera uma representação textual determinista da consulta e das
    entradas.
    """

    query: str
    entries: tuple[ContextEntry, ...]

    def text(self) -> str:
        """Representação textual estável do pacote de contexto."""
        linhas = [f"CONSULTA: {self.query}"]
        for posicao, entrada in enumerate(self.entries, start=1):
            linhas.append("")
            linhas.append(f"{posicao}. [{entrada.record_id}] {entrada.title}")
            linhas.append(f"   {entrada.snippet}")
            if entrada.source:
                linhas.append(f"   Fonte: {entrada.source}")
            if entrada.tags:
                linhas.append(f"   Etiquetas: {', '.join(entrada.tags)}")
        return "\n".join(linhas)


class ContextBuilder:
    """Constrói pacotes de contexto a partir de um índice em memória.

    Deterministica e sem estado: dada uma consulta e um ``KnowledgeIndex``
    (9.4), devolve ``KnowledgeContext`` com as ``top`` entradas mais
    relevantes e excertos truncados de forma fixa.
    """

    def build(
        self,
        consulta: str,
        indice: KnowledgeIndex,
        *,
        top: int = 5,
        snippet_caracteres: int = 280,
    ) -> KnowledgeContext:
        """Monta o contexto para ``consulta`` usando o ``indice``.

        Args:
            consulta: termos da pesquisa (normalizados pelo índice).
            indice: índice invertido já com os registos perspectivados.
            top: número máximo de entradas a incluir.
            snippet_caracteres: comprimento máximo do excerto.

        Returns:
            Pacote de contexto com entradas ordenadas por relevância.
        """
        resultados = indice.search(consulta, limit=top)
        entradas = tuple(
            self._entrada(registo, snippet_caracteres) for registo, _ in resultados
        )
        return KnowledgeContext(query=consulta, entries=entradas)

    @staticmethod
    def _entrada(registo: KnowledgeRecord, comprimento: int) -> ContextEntry:
        """Constrói a entrada de contexto de um registo, sem I/O."""
        return ContextEntry(
            record_id=registo.id,
            title=registo.title,
            snippet=ContextBuilder._excerto(registo.content, comprimento),
            source=registo.metadata.source,
            tags=registo.metadata.tags,
        )

    @staticmethod
    def _excerto(conteudo: str, comprimento: int) -> str:
        """Trunca o conteúdo a um comprimento fixo, com elipse final."""
        if len(conteudo) <= comprimento:
            return conteudo
        return conteudo[:comprimento].rstrip() + _ELLIPSIS


__all__ = ["ContextBuilder", "ContextEntry", "KnowledgeContext"]