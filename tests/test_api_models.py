"""Testes do endpoint de modelos da API (Fase 10, API-06).

Cobrem o handler ``models`` (apresentador fino do ``ModelsService``):
serialização JSON dos veredictos de compatibilidade (modelo, estado,
verificações por requisito e capacidades faltantes), serviço injectável
para determinismo, e o transporte stdlib real sobre ``http.server``
(200 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, models
from wsai2.application import ModelsService
from wsai2.capability import create_default_registry as create_capability_registry
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
from wsai2.model import create_default_registry as create_model_registry
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


def _servico_fixo() -> ModelsService:
    return ModelsService(
        model_registry_source=create_model_registry,
        capability_registry_source=create_capability_registry,
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


def test_models_directo_devolve_veredictos_serializaveis() -> None:
    """API-06: ``models`` apresenta os veredictos reais em JSON puro (200)."""
    resposta = models(ApiRequest(method="GET", path="/models"))
    assert resposta.status == 200
    assert set(resposta.payload) == {"summary", "counts", "verdicts"}
    veredictos = resposta.payload["verdicts"]
    assert isinstance(veredictos, list)
    assert len(veredictos) == 3
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_models_com_servico_injectado() -> None:
    """API-06: o serviço é injectável para resultados deterministas."""
    resposta = models(
        ApiRequest(method="GET", path="/models"),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["summary"] == (
        "3 modelos, 3 disponíveis, 0 condicionados, 0 indisponíveis"
    )
    assert resposta.payload["counts"] == {
        "available": 3,
        "restricted": 0,
        "unavailable": 0,
    }


def test_models_serializa_veredictos_do_relatorio() -> None:
    """API-06: cada veredicto expõe modelo, estado e campos estáveis em JSON."""
    resposta = models(
        ApiRequest(method="GET", path="/models"),
        service=_servico_fixo(),
    )
    ids = {v["model_id"] for v in resposta.payload["verdicts"]}
    assert ids == {"qwen2.5-7b-instruct", "phi-3-mini", "all-MiniLM-L6-v2"}
    for veredicto in resposta.payload["verdicts"]:
        assert set(veredicto) == {
            "model_id",
            "state",
            "is_available",
            "summary",
            "checks",
            "missing_capabilities",
        }
        assert veredicto["state"] == "available"
        assert veredicto["is_available"] is True
        assert veredicto["missing_capabilities"] == []


def test_models_serializa_checks_e_required_capabilities() -> None:
    """API-06: checks incluem required_capabilities convertidas em listas JSON."""
    resposta = models(
        ApiRequest(method="GET", path="/models"),
        service=_servico_fixo(),
    )
    qwen = [v for v in resposta.payload["verdicts"] if v["model_id"] == "qwen2.5-7b-instruct"][0]
    capacidades_check = [c for c in qwen["checks"] if c["name"] == "capabilities"][0]
    assert capacidades_check["required"] == ["local_llm_inference"]
    assert capacidades_check["available"] == ["local_llm_inference"]
    assert capacidades_check["satisfied"] is True
    assert isinstance(qwen["checks"], list)
    for check in qwen["checks"]:
        assert check["satisfied"] is True
        assert "required" in check and "available" in check


def test_models_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/models")
    assert status == 200
    assert "summary" in payload
    assert "counts" in payload
    assert "verdicts" in payload


def test_models_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/models", metodo="POST")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}