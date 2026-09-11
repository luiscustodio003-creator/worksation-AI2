"""Testes do endpoint de capacidades da API (Fase 10, API-05).

Cobrem o handler ``capabilities`` (apresentador fino do
``CapabilitiesService``): serialização JSON do relatório de
compatibilidade (estado, justificação e verificação por requisito),
serviço injectável para determinismo, e o transporte stdlib real sobre
``http.server`` (200 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, capabilities
from wsai2.application import CapabilitiesService
from wsai2.capability import create_default_registry
from wsai2.hardware import (
    Architecture,
    CapabilityDomain,
    CapabilityLevel,
    CpuInfo,
    CpuVendor,
    GpuInfo,
    HardwareCapability,
    HardwareProfile,
    MemoryInfo,
    StorageInfo,
)
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile


def _perfil_hardware_fixo() -> HardwareProfile:
    return HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL,
            model_name="Core i9",
            architecture=Architecture.X86_64,
            physical_cores=8,
            logical_cores=16,
            max_frequency_mhz=5000.0,
            cache_l1_kb=1024,
            cache_l2_kb=16384,
            cache_l3_kb=32768,
            features=("avx2", "avx512f"),
        ),
        memory=MemoryInfo(total_bytes=64 * 1024**3, swap_total_bytes=8 * 1024**3),
        gpus=(
            GpuInfo(
                name="RTX 4090",
                vendor="nvidia",
                vram_bytes=24 * 1024**3,
                driver_version="1.0",
            ),
        ),
        storage=(
            StorageInfo(
                device_path="C:\\",
                total_bytes=2 * 1024**4,
                type="nvme",
                mount_point="C:",
            ),
        ),
        capabilities=(
            HardwareCapability(
                domain=CapabilityDomain.COMPUTE,
                score=1.0,
                level=CapabilityLevel.HIGH_END,
                details={"physical_cores": 8},
            ),
            HardwareCapability(
                domain=CapabilityDomain.GRAPHICS,
                score=1.0,
                level=CapabilityLevel.HIGH_END,
                details={"gpu_count": 1},
            ),
        ),
        overall_level=CapabilityLevel.HIGH_END,
    )


def _perfil_runtime_fixo() -> RuntimeProfile:
    return RuntimeProfile(
        cpu=CpuLoad(percent=10.0, count=8),
        memory=MemoryRuntime(
            total_bytes=64 * 1024**3,
            available_bytes=48 * 1024**3,
            used_bytes=16 * 1024**3,
            percent=25.0,
        ),
    )


def _servico_fixo() -> CapabilitiesService:
    return CapabilitiesService(
        registry_source=create_default_registry,
        hardware_source=_perfil_hardware_fixo,
        runtime_source=_perfil_runtime_fixo,
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


def test_capabilities_directo_devolve_relatorio_serializavel() -> None:
    """API-05: ``capabilities`` apresenta o relatório real em JSON puro (200)."""
    resposta = capabilities(ApiRequest(method="GET", path="/capabilities"))
    assert resposta.status == 200
    assert set(resposta.payload) == {"summary", "counts", "entries"}
    contagens = resposta.payload["counts"]
    assert isinstance(contagens, dict)
    assert contagens["available"] > 0
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_capabilities_com_servico_injectado() -> None:
    """API-05: o serviço é injectável para resultados deterministas."""
    resposta = capabilities(
        ApiRequest(method="GET", path="/capabilities"),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["summary"] == (
        "4 capacidades disponíveis, 0 condicionadas, 0 indisponíveis"
    )
    assert resposta.payload["counts"] == {
        "available": 4,
        "restricted": 0,
        "unavailable": 0,
    }


def test_capabilities_serializa_entradas_do_relatorio() -> None:
    """API-05: cada entrada expõe definição, estado e justificação em JSON."""
    resposta = capabilities(
        ApiRequest(method="GET", path="/capabilities"),
        service=_servico_fixo(),
    )
    entradas = resposta.payload["entries"]
    assert isinstance(entradas, list)
    assert len(entradas) == 4
    for entrada in entradas:
        assert set(entrada) == {
            "id",
            "name",
            "description",
            "domain",
            "state",
            "is_available",
            "justification",
            "requirements",
            "checks",
        }
        assert entrada["domain"] in {"compute", "graphics"}
        assert entrada["state"] == "available"
        assert entrada["is_available"] is True
        assert isinstance(entrada["justification"], str)


def test_capabilities_serializa_requisitos_e_checks() -> None:
    """API-05: requisitos e verificações por requisito em JSON puro."""
    resposta = capabilities(
        ApiRequest(method="GET", path="/capabilities"),
        service=_servico_fixo(),
    )
    leves = [
        entrada
        for entrada in resposta.payload["entries"]
        if entrada["id"] == "lightweight_processing"
    ][0]
    assert leves["requirements"] == {
        "min_ram_gb": 1.0,
        "min_vram_gb": None,
        "min_cpu_cores": 1,
        "requires_gpu": False,
        "min_available_disk_gb": 0.0,
    }
    nomes = [check["name"] for check in leves["checks"]]
    assert nomes == ["ram_total", "ram_available", "cpu_cores", "disk"]
    for check in leves["checks"]:
        assert check["satisfied"] is True
        assert "required" in check and "available" in check


def test_capabilities_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/capabilities")
    assert status == 200
    assert "summary" in payload
    assert "counts" in payload
    assert "entries" in payload


def test_capabilities_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/capabilities", metodo="POST")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}