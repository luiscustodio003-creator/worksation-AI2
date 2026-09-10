"""Testes do subsistema API (Fase 10, API-01).

Cobrem o contrato de mensagens (imutáveis), o ``ApiGateway`` por handle
directo (rota/método) e o transporte stdlib sobre ``http.server`` num
servidor real em loopback com porta efémera (200/404/405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import (
    ApiGateway,
    ApiRequest,
    ApiResponse,
    StdLibHttpGateway,
    health,
)


@pytest.fixture()
def gateway_http() -> tuple[StdLibHttpGateway, str, int]:
    gateway = StdLibHttpGateway()
    host, port = gateway.serve("127.0.0.1", 0)
    yield gateway, host, port
    gateway.shutdown()


def _requisicao(base: str, rota: str, metodo: str = "GET") -> tuple[int, dict[str, object]]:
    pedido = urllib.request.Request(f"{base}{rota}", method=metodo)
    try:
        with urllib.request.urlopen(pedido, timeout=5) as resposta:
            return resposta.status, json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read().decode("utf-8"))


def test_contrato_de_mensagens_imutavel() -> None:
    pedido = ApiRequest(method="GET", path="/health")
    resposta = ApiResponse(status=200, payload={"status": "ok"})
    assert pedido.headers == {}
    assert pedido.body == ""
    assert resposta.headers == {}
    with pytest.raises(AttributeError):
        pedido.method = "POST"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        resposta.status = 404  # type: ignore[misc]


def test_health_endpoint(gateway_http: tuple[StdLibHttpGateway, str, int]) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/health")
    assert status == 200
    assert payload == {
        "api": "1.0",
        "core": "1.0",
        "status": "ok",
    }


def test_rota_inexistente_devolve_404(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/inexistente")
    assert status == 404
    assert payload == {"error": "rota inexistente"}


def test_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/health", metodo="POST")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}


def test_handle_directo_rota_e_metodo() -> None:
    gateway: ApiGateway = StdLibHttpGateway()
    ok = gateway.handle(ApiRequest(method="GET", path="/health"))
    assert isinstance(ok, ApiResponse)
    assert ok.status == 200
    assert ok.payload["status"] == "ok"

    neg = gateway.handle(ApiRequest(method="POST", path="/health"))
    assert neg.status == 405

    inexistente = gateway.handle(ApiRequest(method="GET", path="/ausente"))
    assert inexistente.status == 404


def test_health_e_funcao_pura_sem_transporte() -> None:
    resposta = health(ApiRequest(method="GET", path="/health"))
    assert resposta.status == 200
    assert resposta.payload["api"] == "1.0"
    assert resposta.payload["core"] == "1.0"