"""Endpoint de contexto de conhecimento da API (API-08).

Apresenta o use-case ``KnowledgeContextService`` (APP-09) sobre HTTP:
transforma o ``KnowledgeContextResponse`` da camada Application num
``ApiResponse`` com payload serializável em JSON (consultas de conhecimento
e o pacote de contexto construído). O handler é um apresentador fino — não
contém lógica de domínio nem I/O próprio: delega a recolha no serviço, que
pode ser injectado para testes deterministas. Dependência arquitectural:
``api -> application`` (com a aresta ``api -> knowledge`` para o enum de
tipo de conhecimento, análoga a ``api -> task`` na API-07).

Tal como ``/tasks``, o endpoint aceita ``POST`` com um corpo JSON que
descreve a consulta (``query``, ``limit`` e ``kind`` opcional).
"""

from __future__ import annotations

import json

from wsai2.application import (
    KnowledgeContextRequest,
    KnowledgeContextResponse,
    KnowledgeContextService,
)
from wsai2.knowledge import KnowledgeKind, KnowledgeRecord

from .contract import ApiRequest, ApiResponse

_KIND_MAP: dict[str, KnowledgeKind] = {kind.value: kind for kind in KnowledgeKind}


def knowledge(
    request: ApiRequest,
    service: KnowledgeContextService | None = None,
) -> ApiResponse:
    """Endpoint ``POST /knowledge``: contexto de conhecimento para uma consulta.

    Recebe o corpo JSON com a consulta, constrói o ``KnowledgeContextRequest``
    e devolve as correspondências e o contexto serializados em JSON. Um
    ``KnowledgeContextService`` pode ser injectado para testes deterministas.
    O método/rota são validados pelo gateway; aqui assume-se
    ``POST /knowledge`` já resolvido.
    """
    dados = _parsear_body(request)
    if isinstance(dados, ApiResponse):
        return dados

    pedido = _construir_pedido(dados)
    if isinstance(pedido, ApiResponse):
        return pedido

    servico = service if service is not None else KnowledgeContextService()
    resposta: KnowledgeContextResponse = servico.resolve(pedido)
    return ApiResponse(status=200, payload=_resposta_para_payload(resposta))


def _parsear_body(request: ApiRequest) -> dict[str, object] | ApiResponse:
    """Extrai e valida o corpo JSON do pedido."""
    if not request.body.strip():
        return ApiResponse(status=400, payload={"error": "body vazio: JSON esperado"})
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return ApiResponse(status=400, payload={"error": "body invalido: JSON esperado"})
    if not isinstance(dados, dict):
        return ApiResponse(status=400, payload={"error": "body invalido: objecto JSON esperado"})
    return dados


def _construir_pedido(dados: dict[str, object]) -> KnowledgeContextRequest | ApiResponse:
    """Constrói o ``KnowledgeContextRequest`` a partir dos dados do pedido."""
    try:
        query = dados.get("query", "")
        limit = dados.get("limit", 8)
        kind_valor = dados.get("kind")
        if kind_valor is not None:
            kind = _KIND_MAP.get(str(kind_valor))
            if kind is None:
                return ApiResponse(
                    status=400,
                    payload={
                        "error": (
                            f"kind invalido: {kind_valor!r}. "
                            f"Valores aceites: {', '.join(_KIND_MAP)}"
                        )
                    },
                )
        else:
            kind = None

        pedido = KnowledgeContextRequest(
            query=str(query),
            limit=int(limit),
            kind=kind,
        )
    except (TypeError, ValueError) as exc:
        return ApiResponse(status=400, payload={"error": f"pedido invalido: {exc}"})
    return pedido


def _resposta_para_payload(resposta: KnowledgeContextResponse) -> dict[str, object]:
    """Serializa o ``KnowledgeContextResponse`` em JSON puro."""
    payload: dict[str, object] = {
        "query": resposta.query,
        "matches": [_registro_para_payload(registo) for registo in resposta.matches],
    }
    if resposta.context is not None:
        payload["context"] = {
            "query": resposta.context.query,
            "entries": [
                {
                    "record_id": entrada.record_id,
                    "title": entrada.title,
                    "snippet": entrada.snippet,
                    "source": entrada.source,
                    "tags": list(entrada.tags),
                }
                for entrada in resposta.context.entries
            ],
            "text": resposta.context.text(),
        }
    else:
        payload["context"] = None
    return payload


def _registro_para_payload(registo: KnowledgeRecord) -> dict[str, object]:
    """Serializa um ``KnowledgeRecord`` em JSON puro."""
    return {
        "id": registo.id,
        "title": registo.title,
        "content": registo.content,
        "kind": registo.kind.value,
        "metadata": {
            "source": registo.metadata.source,
            "language": registo.metadata.language,
            "author": registo.metadata.author,
            "tags": list(registo.metadata.tags),
            "extras": dict(registo.metadata.extras),
        },
        "created_at": registo.created_at,
    }


__all__ = ["knowledge"]