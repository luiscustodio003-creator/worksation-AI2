"""Extracção heurística de metadados de conhecimento (Fase 9.3).

Deriva ``KnowledgeMetadata`` estruturado a partir do conteúdo e da
proveniência de um ``KnowledgeRecord`` válido: idioma (detecção
heurística por marcadores), etiquetas (termos frequentes com exclusão de
palavras de ligação) e proveniência (preservada do que já estiver
declarado). A extracção semântica via Model/Provider NÃO é feita aqui —
fica para unidade posterior com decisão própria, junto da indexação.

Responsabilidade única desta unidade: produzir metadados deterministas.
Sem I/O, sem rede, sem modelos e sem estado persistente.
"""

from __future__ import annotations

from collections import Counter
import re

from .base import KnowledgeMetadata, KnowledgeRecord

_PALAVRA = re.compile(r"[a-zà-ÿ]{3,}")
_MARCADOR = re.compile(r"[a-zà-ÿ]{2,}")

# Marcadores por idioma (palavras frequentes de função). A detecção é
# heurística e determinista; o projecto é em português de Portugal, por
# isso o marcador PT é o mais completo.
_MARCADORES: dict[str, frozenset[str]] = {
    "pt-PT": frozenset(
        {
            "de", "da", "do", "das", "dos", "e", "que", "em", "para",
            "com", "uma", "o", "a", "os", "as", "é", "por", "na", "no",
            "pelo", "pela", "num", "este", "esta", "não", "mais", "também",
        }
    ),
    "en": frozenset(
        {
            "the", "and", "of", "to", "in", "for", "with", "on", "is",
            "are", "this", "that", "from", "by", "not", "more", "also",
        }
    ),
}

# Palavras de ligação excluídas na extracção de etiquetas (pt + en).
_EXCLUIDAS_TAGS: frozenset[str] = frozenset(
    {
        # pt
        "de", "da", "do", "das", "dos", "e", "que", "em", "para", "com",
        "uma", "um", "o", "a", "os", "as", "é", "por", "na", "no", "não",
        "mais", "mas", "se", "ao", "aos", "pelo", "pela", "este", "esta",
        "estes", "estas", "como", "ser", "tem", "ter", "são", "foi", "será",
        # en
        "the", "and", "of", "to", "in", "for", "with", "on", "is", "are",
        "that", "from", "by", "this", "has", "have", "will", "was", "be",
        "it", "as", "an", "at",
    }
)

_IDIOMA_INDETERMINADO = "und"


def detect_language(content: str) -> str:
    """Detecta o idioma do conteúdo por marcadores frequentes.

    Devolve um código de idioma ("pt-PT", "en") ou ``"und"`` quando não é
    possível decidir com confiança (sem marcadores ou empate).
    """
    tokens = _MARCADOR.findall(content.casefold())
    if not tokens:
        return _IDIOMA_INDETERMINADO
    contagens = {
        idioma: sum(1 for token in tokens if token in marcadores)
        for idioma, marcadores in _MARCADORES.items()
    }
    ordenadas = sorted(contagens.items(), key=lambda par: par[1], reverse=True)
    primeiro, segundo = ordenadas[0], ordenadas[1]
    if primeiro[1] == 0 or primeiro[1] == segundo[1]:
        return _IDIOMA_INDETERMINADO
    return primeiro[0]


def derive_tags(content: str, *, limit: int = 8) -> tuple[str, ...]:
    """Deriva etiquetas por frequência de termos, excluindo as de ligação.

    Devolve os termos mais frequentes (≥ 3 letras, sem acentuar duplicado)
    ordenados por frequência decrescente e alfabeticamente em caso de
    empate. Limite de ``limit`` etiquetas por omissão.
    """
    tokens = [token for token in _PALAVRA.findall(content.casefold()) if token not in _EXCLUIDAS_TAGS]
    if not tokens:
        return ()
    frequencias = Counter(tokens)
    ordenados = sorted(frequencias.items(), key=lambda par: (-par[1], par[0]))
    return tuple(token for token, _ in ordenados[:limit])


def _merge_tags(explicitas: tuple[str, ...], derivadas: tuple[str, ...]) -> tuple[str, ...]:
    """Junta etiquetas explícitas e derivadas sem duplicar (preserva ordem)."""
    resultado = list(dict.fromkeys([*explicitas, *derivadas]))
    return tuple(resultado)


class KnowledgeMetadataExtractor:
    """Deriva metadados estruturados a partir de um registo de conhecimento.

    Preenche o que estiver em falta (idioma e etiquetas, por heurística)
    e preserva a proveniência já declarada (``source``, ``author``,
    ``extras`` e etiquetas explícitas). É determinista, sem estado e sem
    I/O — a extracção semântica fica para unidade posterior.
    """

    def extract(self, record: KnowledgeRecord, *, tags: int = 8) -> KnowledgeMetadata:
        """Deriva e devolve os metadados do registo.

        Args:
            record: registo de conhecimento já válido (contrato 9.1).
            tags: número máximo de etiquetas derivadas a considerar.

        Returns:
            Metadados com idioma e etiquetas completados e proveniência
            preservada.
        """
        declarado = record.metadata
        idioma = declarado.language or detect_language(record.content)
        etiquetas = _merge_tags(declarado.tags, derive_tags(record.content, limit=tags))
        return KnowledgeMetadata(
            source=declarado.source,
            language=idioma,
            author=declarado.author,
            tags=etiquetas,
            extras=dict(declarado.extras),
        )


__all__ = ["KnowledgeMetadataExtractor", "detect_language", "derive_tags"]