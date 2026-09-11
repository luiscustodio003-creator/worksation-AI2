"""Testes do endpoint de hardware da API (Fase 10, API-03).

Cobrem o handler ``hardware`` (apresentador fino do
``HardwareProfileService``): serialização JSON do perfil estrutural
(cpu, memória, gpus, armazenamento e capacidades), serviço injectável
para determinismo, e o transporte stdlib real sobre ``http.server``
(200 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, hardware
from wsai2.application import HardwareProfileService
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


def _perfil_fixo() -> HardwareProfile:
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
                domain=CapabilityDomain.MEMORY,
                score=1.0,
                level=CapabilityLevel.HIGH_END,
                details={"total_gb": 64.0},
            ),
            HardwareCapability(
                domain=CapabilityDomain.GRAPHICS,
                score=1.0,
                level=CapabilityLevel.HIGH_END,
                details={"gpu_count": 1},
            ),
            HardwareCapability(
                domain=CapabilityDomain.STORAGE,
                score=0.9,
                level=CapabilityLevel.HIGH_END,
                details={"total_gb": 2048.0},
            ),
        ),
        overall_level=CapabilityLevel.HIGH_END,
    )


def _servico_fixo() -> HardwareProfileService:
    perfil = _perfil_fixo()
    return HardwareProfileService(profile_source=lambda: perfil)


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


def test_hardware_directo_devolve_perfil_serializavel() -> None:
    """API-03: ``hardware`` apresenta o perfil real em JSON puro (200)."""
    resposta = hardware(ApiRequest(method="GET", path="/hardware"))
    assert resposta.status == 200
    assert set(resposta.payload) == {
        "overall_level",
        "cpu_summary",
        "memory_summary",
        "gpu_summary",
        "storage_summary",
        "cpu",
        "memory",
        "gpus",
        "storage",
        "capabilities",
    }
    cpu = resposta.payload["cpu"]
    assert isinstance(cpu, dict)
    assert cpu["physical_cores"] > 0
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_hardware_com_servico_injectado() -> None:
    """API-03: o serviço é injectável para resultados deterministas."""
    resposta = hardware(
        ApiRequest(method="GET", path="/hardware"),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["overall_level"] == "high_end"
    cpu = resposta.payload["cpu"]
    assert isinstance(cpu, dict)
    assert cpu["vendor"] == "intel"
    assert cpu["architecture"] == "x86_64"
    assert cpu["features"] == ["avx2", "avx512f"]
    memoria = resposta.payload["memory"]
    assert isinstance(memoria, dict)
    assert memoria["total_gb"] == 64.0


def test_hardware_serializa_gpus_e_armazenamento() -> None:
    """API-03: gpus e armazenamento são listas JSON com campos estáveis."""
    resposta = hardware(
        ApiRequest(method="GET", path="/hardware"),
        service=_servico_fixo(),
    )
    gpus = resposta.payload["gpus"]
    assert gpus == [
        {
            "name": "RTX 4090",
            "vendor": "nvidia",
            "vram_bytes": 24 * 1024**3,
            "driver_version": "1.0",
        }
    ]
    armazenamento = resposta.payload["storage"]
    assert armazenamento == [
        {
            "device_path": "C:\\",
            "total_bytes": 2 * 1024**4,
            "type": "nvme",
            "mount_point": "C:",
        }
    ]


def test_hardware_serializa_capacidades_derivadas() -> None:
    """API-03: capacidades expõem domínio, score e nível em JSON."""
    resposta = hardware(
        ApiRequest(method="GET", path="/hardware"),
        service=_servico_fixo(),
    )
    capacidades = resposta.payload["capabilities"]
    assert isinstance(capacidades, list)
    dominios = [cap["domain"] for cap in capacidades]
    assert dominios == ["compute", "memory", "graphics", "storage"]
    for cap in capacidades:
        assert cap["score"] >= 0.0
        assert cap["level"] == "high_end"
        assert isinstance(cap["details"], dict)


def test_hardware_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/hardware")
    assert status == 200
    assert "overall_level" in payload
    assert "cpu" in payload
    assert "capabilities" in payload


def test_hardware_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/hardware", metodo="POST")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}