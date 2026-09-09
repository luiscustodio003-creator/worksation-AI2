"""Indexação em memória de conhecimento (Fase 9.4).

Decisão documentada (2026-09-09 — ver `PROJECT_STATE.md`, unidade 9.4 e
`docs/knowledge/BASE-40-knowledge-in-memory-index.md`): o índice é
construído e interrogado integralmente em memória — determinista,
reversível e sem I/O, persistência ou embeddings. A estratégia de
armazenamento persistente e/ou embeddings da recuperação fica para a
unidade 9.5, com decisão própria, antes de qualquer persistência.

Responsabilidade única desta unidade: mapear termos normalizados →
frequência por campo/registo (título, etiquetas, conteúdo) e responder a
consultas por termos com ordenação determinista.
"""

from __future__ import annotations

from .base import KnowledgeRecord
from .metadata import tokenize
from .registry import KnowledgeRegistry

_PESO_TITULO = 3
_PESO_ETIQUETAS = 2
_PESO_CONTEUDO = 1

_CAMPOS = {
    "title": _PESO_TITULO,
    "tags": _PESO_ETIQUETAS,
    "content": _PESO_CONTEUDO,
}


class KnowledgeIndex:
    """Índice invertido, em memória, sobre registos de conhecimento.

    Não persiste, não recorre a embeddings e não depende de I/O. A
    admissão e a consulta usam a mesma normalização de termos do resto do
    subsistema (idioma/etiquetas), garantindo coerência na busca.
    """

    def __init__(self) -> None:
        self._frequencias: dict[str, dict[str, dict[str, int]]] = {
            campo: {} for campo in _CAMPOS
        }
        self._registos: dict[str, KnowledgeRecord] = {}

    def __len__(self) -> int:
        """Número de registos indexados."""
        return len(self._registos)

    def index(self, registo: KnowledgeRecord) -> None:
        """Adiciona ou substitui um registo no índice.

        Se a identidade já estiver indexada, remove as entradas antigas
        antes de registar o novo conteúdo, evitando pontuações acumuladas.
        """
        if registo.id in self._registos:
            self.unindex(registo.id)
        self._registos[registo.id] = registo
        for campo in _CAMPOS:
            texto = self._texto_do_campo(registo, campo)
            terminos = self._frequencias[campo]
            for termo in tokenize(texto):
                por_registo = terminos.setdefault(termo, {})
                por_registo[registo.id] = por_registo.get(registo.id, 0) + 1

    def unindex(self, register_id: str) -> bool:
        """Remove um registo do índice.

        Devolve ``True`` se o registo estava indexado.
        """
        if register_id not in self._registos:
            return False
        del self._registos[register_id]
        for terminos in self._frequencias.values():
            for termo in list(terminos.keys()):
                por_registo = terminos[termo]
                por_registo.pop(register_id, None)
                if not por_registo:
                    del terminos[termo]
        return True

    def build(self, registos: KnowledgeRegistry) -> None:
        """Indexa todos os registos de um registo de conhecimento."""
        for registo in registos.all():
            self.index(registo)

    def search(self, consulta: str, *, limit: int = 8) -> tuple[tuple[KnowledgeRecord, int], ...]:
        """Responde a uma consulta por termos, com ordenação determinista.

        A pontuação de cada registo é a soma, para cada termo da consulta,
        da frequência no campo multiplicada pelo peso do campo (título 3,
        etiquetas 2, conteúdo 1). Empates são desfeitos pela ordem
        alfabética do ``id``.

        Returns:
            Tuplo ``(registro, pontuação)`` ordenado por pontuação
            decrescente (e por ``id`` em caso de empate), até ``limit``.
        """
        termos = tokenize(consulta)
        if not termos:
            return ()
        pontuacoes: dict[str, int] = {}
        for termo in termos:
            for campo, peso in _CAMPOS.items():
                por_registo = self._frequencias[campo].get(termo, {})
                for register_id, frequencia in por_registo.items():
                    pontuacoes[register_id] = (
                        pontuacoes.get(register_id, 0) + frequencia * peso
                    )
        if not pontuacoes:
            return ()
        ordenados = sorted(pontuacoes.items(), key=lambda par: (-par[1], par[0]))
        return tuple(
            (self._registos[register_id], pontuacao)
            for register_id, pontuacao in ordenados[:limit]
        )

    @staticmethod
    def _texto_do_campo(registo: KnowledgeRecord, campo: str) -> str:
        """Texto indexável de um campo do registo."""
        if campo == "title":
            return registo.title
        if campo == "tags":
            return " ".join(registo.metadata.tags)
        return registo.content


__all__ = ["KnowledgeIndex"]