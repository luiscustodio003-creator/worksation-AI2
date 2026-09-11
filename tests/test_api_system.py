"""Testes do endpoint de sistema da API (Fase 10, API-02).

Cobrem o handler ``system`` (apresentador fino do ``SystemInfoService``):
serialização JSON da plataforma e do uptime, serviço injectável para
determinismo, e o transporte stdlib real sobre ``http.server``
(200 / 405 / payload estável).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, system
from wsai2.application import SystemInfoService
from wsai2.platform import (
    OperatingSystem,
    PlatformInfo,
    PlatformName,
)
from wsai2.runtime import SystemUptime


def _plataforma_fixa() -> PlatformInfo:
    return PlatformInfo(
        os=OperatingSystem.WINDOWS,
        name=PlatformName.WINDOWS.value,
        release="10",
        version="10.0.19045",
        machine="x86_64",
    )


class _ProviderFixo:
    def detect(self) -> PlatformInfo:
        return _plataforma_fixa()


def _uptime_fixo() -> SystemUptime:
    return SystemUptime(boot_timestamp=1000.0, uptime_seconds=3600.0)


def _servico_fixo() -> SystemInfoService:
    return SystemInfoService(
        provider=_ProviderFixo(), uptime_source=lambda: _uptime_fixo()
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


def test_system_directo_devolve_plataforma_serializavel() -> None:
    """API-02: ``system`` apresenta a plataforma real em JSON puro (200)."""
    resposta = system(ApiRequest(method="GET", path="/system"))
    assert resposta.status == 200
    plataforma = resposta.payload["platform"]
    assert isinstance(plataforma, dict)
    assert set(plataforma) == {"os", "name", "release", "version", "machine"}
    assert plataforma["os"] in {"windows", "linux", "macos", "unknown"}
    assert plataforma["name"]
    uptime = resposta.payload["uptime"]
    assert uptime is None or isinstance(uptime, dict)


def test_system_com_servico_injectado() -> None:
    """API-02: o serviço é injectável para resultados deterministas."""
    resposta = system(
        ApiRequest(method="GET", path="/system"),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["platform"] == {
        "os": "windows",
        "name": "windows",
        "release": "10",
        "version": "10.0.19045",
        "machine": "x86_64",
    }


def test_system_serializa_uptime_completo() -> None:
    """API-02: o uptime presente é devolvido com todos os campos seriais."""
    resposta = system(
        ApiRequest(method="GET", path="/system"),
        service=_servico_fixo(),
    )
    assert resposta.payload["uptime"] == {
        "boot_timestamp": 1000.0,
        "uptime_seconds": 3600.0,
        "uptime_hours": 1.0,
        "uptime_days": 3600.0 / 86400.0,
    }


def test_system_uptime_ausente_devolve_none() -> None:
    """API-02: sem uptime, o contrato JSON devolve ``null`` (estável)."""
    servico = SystemInfoService(provider=_ProviderFixo(), uptime_source=lambda: None)
    resposta = system(
        ApiRequest(method="GET", path="/system"),
        service=servico,
    )
    assert resposta.payload["uptime"] is None


def test_system_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/system")
    assert status == 200
    plataforma = payload["platform"]
    assert isinstance(plataforma, dict)
    assert set(plataforma) == {"os", "name", "release", "version", "machine"}
    assert "uptime" in payload


def test_system_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/system", metodo="POST")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}