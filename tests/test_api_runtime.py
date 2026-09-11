"""Testes do endpoint de runtime da API (Fase 10, API-04).

Cobrem o handler ``runtime`` (apresentador fino do
``RuntimeProfileService``): serialização JSON do estado momentâneo
(CPU, memória, processos, uptime, disponibilidade e top process),
serviço injectável para determinismo, e o transporte stdlib real sobre
``http.server`` (200 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, runtime
from wsai2.application import RuntimeProfileService
from wsai2.runtime import (
    AvailabilityDomain,
    AvailabilityStatus,
    CpuLoad,
    MemoryRuntime,
    ProcessInfo,
    RuntimeAvailability,
    RuntimeProfile,
    SystemUptime,
)


def _perfil_fixo() -> RuntimeProfile:
    return RuntimeProfile(
        cpu=CpuLoad(
            percent=35.0,
            per_core=(30.0, 40.0),
            count=8,
            frequency_current_mhz=4200.0,
        ),
        memory=MemoryRuntime(
            total_bytes=64 * 1024**3,
            available_bytes=32 * 1024**3,
            used_bytes=32 * 1024**3,
            percent=50.0,
            swap_total_bytes=8 * 1024**3,
            swap_used_bytes=1024**3,
            swap_percent=12.5,
        ),
        processes=(
            ProcessInfo(
                pid=1,
                name="python",
                status="running",
                cpu_percent=2.5,
                memory_rss_bytes=256 * 1024**2,
                memory_percent=1.0,
            ),
            ProcessInfo(
                pid=2,
                name="kernel",
                status="sleeping",
                cpu_percent=0.0,
                memory_rss_bytes=512 * 1024**2,
                memory_percent=2.0,
            ),
        ),
        uptime=SystemUptime(boot_timestamp=1000.0, uptime_seconds=3600.0),
        availability=(
            RuntimeAvailability(
                domain=AvailabilityDomain.CPU,
                score=0.65,
                status=AvailabilityStatus.HEALTHY,
                details={"load": 35.0},
            ),
            RuntimeAvailability(
                domain=AvailabilityDomain.MEMORY,
                score=0.5,
                status=AvailabilityStatus.DEGRADED,
                details={"percent": 50.0},
            ),
        ),
        overall_status=AvailabilityStatus.HEALTHY,
    )


def _servico_fixo() -> RuntimeProfileService:
    perfil = _perfil_fixo()
    return RuntimeProfileService(profile_source=lambda: perfil)


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


def test_runtime_directo_devolve_estado_serializavel() -> None:
    """API-04: ``runtime`` apresenta o estado real em JSON puro (200)."""
    resposta = runtime(ApiRequest(method="GET", path="/runtime"))
    assert resposta.status == 200
    assert set(resposta.payload) == {
        "overall_status",
        "cpu_summary",
        "memory_summary",
        "uptime_summary",
        "availability_summary",
        "cpu",
        "memory",
        "processes",
        "uptime",
        "availability",
        "top_process",
    }
    cpu = resposta.payload["cpu"]
    assert isinstance(cpu, dict)
    assert cpu["count"] > 0
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_runtime_com_servico_injectado() -> None:
    """API-04: o serviço é injectável para resultados deterministas."""
    resposta = runtime(
        ApiRequest(method="GET", path="/runtime"),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["overall_status"] == "healthy"
    cpu = resposta.payload["cpu"]
    assert isinstance(cpu, dict)
    assert cpu["percent"] == 35.0
    assert cpu["per_core"] == [30.0, 40.0]
    assert cpu["is_saturated"] is False
    memoria = resposta.payload["memory"]
    assert isinstance(memoria, dict)
    assert memoria["percent"] == 50.0
    assert memoria["free_percent"] == 50.0
    assert memoria["has_swap_active"] is True


def test_runtime_serializa_processos() -> None:
    """API-04: processos são listas JSON com campos estáveis."""
    resposta = runtime(
        ApiRequest(method="GET", path="/runtime"),
        service=_servico_fixo(),
    )
    processos = resposta.payload["processes"]
    assert processos == [
        {
            "pid": 1,
            "name": "python",
            "status": "running",
            "cpu_percent": 2.5,
            "memory_rss_bytes": 256 * 1024**2,
            "memory_percent": 1.0,
        },
        {
            "pid": 2,
            "name": "kernel",
            "status": "sleeping",
            "cpu_percent": 0.0,
            "memory_rss_bytes": 512 * 1024**2,
            "memory_percent": 2.0,
        },
    ]


def test_runtime_serializa_uptime_e_availability() -> None:
    """API-04: uptime e disponibilidade são serializados em JSON."""
    resposta = runtime(
        ApiRequest(method="GET", path="/runtime"),
        service=_servico_fixo(),
    )
    assert resposta.payload["uptime"] == {
        "boot_timestamp": 1000.0,
        "uptime_seconds": 3600.0,
        "uptime_hours": 1.0,
        "uptime_days": 3600.0 / 86400.0,
    }
    disponibilidade = resposta.payload["availability"]
    assert disponibilidade == [
        {
            "domain": "cpu",
            "score": 0.65,
            "status": "healthy",
            "details": {"load": 35.0},
        },
        {
            "domain": "memory",
            "score": 0.5,
            "status": "degraded",
            "details": {"percent": 50.0},
        },
    ]


def test_runtime_top_process_devolve_maior_rss() -> None:
    """API-04: ``top_process`` identifica o processo com mais memória RSS."""
    resposta = runtime(
        ApiRequest(method="GET", path="/runtime"),
        service=_servico_fixo(),
    )
    topo = resposta.payload["top_process"]
    assert isinstance(topo, dict)
    assert topo["pid"] == 2
    assert topo["name"] == "kernel"


def test_runtime_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/runtime")
    assert status == 200
    assert "overall_status" in payload
    assert "cpu" in payload
    assert "availability" in payload


def test_runtime_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/runtime", metodo="POST")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}