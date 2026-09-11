"""Testes do endpoint de contexto de conhecimento da API (Fase 10, API-08).

Cobrem o handler ``knowledge`` (apresentador fino do
``KnowledgeContextService``): parsing do corpo JSON com a consulta,
serialização JSON das correspondências e do pacote de contexto, filtro por
tipo de conhecimento, tratamento de pedidos inválidos (400), serviço
injectável para determinismo, e o transporte stdlib real sobre
``http.server`` (200 / 400 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, knowledge
from wsai2.application import KnowledgeContextService
from wsai2.knowledge import (
    KnowledgeKind,
    KnowledgeMetadata,
    KnowledgeRecord,
    KnowledgeRegistry,
)


def _registo_fixo() -> KnowledgeRegistry:
    registo = KnowledgeRegistry()
    registo.register(
        KnowledgeRecord(
            id="km.a",
            title="Registo Supremo",
            content="arquitectura modular do WorkStation",
            kind=KnowledgeKind.DOCUMENT,
            metadata=KnowledgeMetadata(
                source="docs/architecture",
                language="pt",
                author="núcleo",
                tags=("arquitectura",),
            ),
        )
    )
    registo.register(
        KnowledgeRecord(
            id="km.b",
            title="Nota de política",
            content="política de segurança por defeito",
            kind=KnowledgeKind.NOTE,
            metadata=KnowledgeMetadata(
                source="docs/policy",
                language="pt",
                tags=("segurança",),
            ),
        )
    )
    return registo


def _servico_fixo() -> KnowledgeContextService:
    return KnowledgeContextService(registry_source=_registo_fixo)


def _corpo_consulta() -> dict[str, object]:
    return {"query": "arquitectura"}


@pytest.fixture()
def gateway_http() -> tuple[StdLibHttpGateway, str, int]:
    gateway = StdLibHttpGateway()
    host, port = gateway.serve("127.0.0.1", 0)
    yield gateway, host, port
    gateway.shutdown()


def _requisicao(
    base: str,
    rota: str,
    metodo: str = "POST",
    corpo: str | None = None,
) -> tuple[int, dict[str, object]]:
    pedido = urllib.request.Request(f"{base}{rota}", method=metodo)
    if corpo is not None:
        dados = corpo.encode("utf-8")
        pedido.add_header("Content-Type", "application/json")
        pedido.data = dados
    try:
        with urllib.request.urlopen(pedido, timeout=15) as resposta:
            return resposta.status, json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read().decode("utf-8"))


def test_knowledge_directo_devolve_contexto_serializavel() -> None:
    """API-08: ``knowledge`` devolve consulta, correspondências e contexto."""
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body=json.dumps(_corpo_consulta()))
    )
    assert resposta.status == 200
    assert set(resposta.payload) == {"query", "matches", "context"}
    assert resposta.payload["query"] == "arquitectura"
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_knowledge_com_servico_injectado() -> None:
    """API-08: o serviço é injectável para resultados deterministas."""
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body=json.dumps(_corpo_consulta())),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    matches = resposta.payload["matches"]
    assert isinstance(matches, list)
    assert [registo["id"] for registo in matches] == ["km.a"]
    registo = matches[0]
    assert registo["kind"] == "document"
    assert registo["metadata"]["source"] == "docs/architecture"


def test_knowledge_serializa_contexto_textual() -> None:
    """API-08: o contexto expõe entradas com título/excerto/fonte e texto."""
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body=json.dumps(_corpo_consulta())),
        service=_servico_fixo(),
    )
    contexto = resposta.payload["context"]
    assert isinstance(contexto, dict)
    assert contexto["query"] == "arquitectura"
    assert isinstance(contexto["entries"], list)
    assert len(contexto["entries"]) >= 1
    entrada = contexto["entries"][0]
    assert entrada["record_id"] == "km.a"
    assert entrada["title"] == "Registo Supremo"
    assert "arquitectura modular" in entrada["snippet"]
    assert entrada["source"] == "docs/architecture"
    assert isinstance(contexto["text"], str)
    assert "km.a" in contexto["text"]


def test_knowledge_filtra_por_tipo_de_conhecimento() -> None:
    """API-08: o filtro ``kind`` restringe as correspondências."""
    corpo = {"query": "política", "kind": "note"}
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body=json.dumps(corpo)),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert [registo["id"] for registo in resposta.payload["matches"]] == ["km.b"]


def test_knowledge_sem_resultados_devolve_contexto_vazio() -> None:
    """API-08: sem correspondências, o contexto é vazio mas válido."""
    corpo = {"query": "inexistente-termo"}
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body=json.dumps(corpo)),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["matches"] == []
    contexto = resposta.payload["context"]
    assert isinstance(contexto, dict)
    assert contexto["entries"] == []
    assert "CONSULTA" in contexto["text"]


def test_knowledge_kind_invalido_devolve_400() -> None:
    """API-08: um ``kind`` desconhecido é rejeitado com 400."""
    corpo = {"query": "arquitectura", "kind": "mágico"}
    resposta = knowledge(ApiRequest(method="POST", path="/knowledge", body=json.dumps(corpo)))
    assert resposta.status == 400
    assert "kind invalido" in resposta.payload["error"]


def test_knowledge_body_mal_formado_devolve_400() -> None:
    """API-08: um corpo não-JSON é rejeitado com 400."""
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body="isto não é JSON{")
    )
    assert resposta.status == 400
    assert "JSON" in resposta.payload["error"]


def test_knowledge_consulta_vazia_devolve_400() -> None:
    """API-08: uma consulta vazia é rejeitada pelo contrato com 400."""
    resposta = knowledge(
        ApiRequest(method="POST", path="/knowledge", body=json.dumps({"query": ""}))
    )
    assert resposta.status == 400
    assert "pedido invalido" in resposta.payload["error"]


def test_knowledge_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(
        f"http://{host}:{port}", "/knowledge", corpo=json.dumps(_corpo_consulta())
    )
    assert status == 200
    assert "query" in payload
    assert "matches" in payload
    assert "context" in payload


def test_knowledge_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/knowledge", metodo="GET")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}