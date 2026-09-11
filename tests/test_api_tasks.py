"""Testes do endpoint de análise de tarefas da API (Fase 10, API-07).

Cobrem o handler ``tasks`` (apresentador fino do
``TaskAnalysisService``): parsing do corpo JSON com a descrição da
tarefa, serialização JSON da análise completa (classificação,
requisitos, selecção de capacidades e plano), tratamento de pedidos
inválidos (400), serviço injectável para determinismo, e o transporte
stdlib real sobre ``http.server`` (200 / 400 / 405).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from wsai2.api import ApiRequest, StdLibHttpGateway, tasks
from wsai2.application import TaskAnalysisService
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


def _servico_fixo() -> TaskAnalysisService:
    return TaskAnalysisService(
        capability_registry_source=create_capability_registry,
        model_registry_source=create_model_registry,
        hardware_source=_perfil_hardware_fixo,
        runtime_source=_perfil_runtime_fixo,
    )


def _corpo_tarefa_chat() -> dict[str, object]:
    return {
        "task_id": "t1",
        "kind": "chat",
        "prompt": "Olá!",
        "max_tokens": 128,
        "required_capabilities": ["local_llm_inference"],
    }


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


def test_tasks_directo_devolve_analise_serializavel() -> None:
    """API-07: ``tasks`` devolve a análise real em JSON puro (200)."""
    resposta = tasks(
        ApiRequest(
            method="POST",
            path="/tasks",
            body=json.dumps(_corpo_tarefa_chat()),
        )
    )
    assert resposta.status == 200
    assert set(resposta.payload) == {
        "task_id",
        "classification",
        "requirements",
        "selection",
        "plan",
    }
    assert resposta.payload["task_id"] == "t1"
    json.dumps(resposta.payload)  # deve ser serializável em JSON


def test_tasks_com_servico_injectado() -> None:
    """API-07: o serviço é injectável para resultados deterministas."""
    resposta = tasks(
        ApiRequest(
            method="POST",
            path="/tasks",
            body=json.dumps(_corpo_tarefa_chat()),
        ),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["task_id"] == "t1"
    assert resposta.payload["classification"] == {
        "task_id": "t1",
        "kind": "chat",
        "category": "chat",
    }
    assert resposta.payload["requirements"] == {
        "task_id": "t1",
        "category": "chat",
        "required_capabilities": ["local_llm_inference"],
        "max_tokens": 128,
    }


def test_tasks_serializa_seleccao_de_capacidades() -> None:
    """API-07: a selecção expõe required/available/missing e viabilidade."""
    resposta = tasks(
        ApiRequest(
            method="POST",
            path="/tasks",
            body=json.dumps(_corpo_tarefa_chat()),
        ),
        service=_servico_fixo(),
    )
    seleccao = resposta.payload["selection"]
    assert isinstance(seleccao, dict)
    assert seleccao["task_id"] == "t1"
    assert seleccao["required"] == ["local_llm_inference"]
    assert "local_llm_inference" in seleccao["available"]
    assert seleccao["missing"] == []
    assert seleccao["is_viable"] is True


def test_tasks_serializa_o_plano_de_execucao() -> None:
    """API-07: o plano expõe categoria, viabilidade, modelo e passos."""
    resposta = tasks(
        ApiRequest(
            method="POST",
            path="/tasks",
            body=json.dumps(_corpo_tarefa_chat()),
        ),
        service=_servico_fixo(),
    )
    plano = resposta.payload["plan"]
    assert isinstance(plano, dict)
    assert plano["task_id"] == "t1"
    assert plano["category"] == "chat"
    assert isinstance(plano["feasible"], bool)
    assert isinstance(plano["model_id"], str) or plano["model_id"] is None
    assert plano["provider_id"] is None  # APP-08 sem fornecedores injectados
    assert isinstance(plano["reasons"], list)
    assert isinstance(plano["steps"], list)
    assert len(plano["steps"]) >= 3
    assert isinstance(plano["is_executable"], bool)


def test_tasks_capacidade_impossivel_fica_inviavel() -> None:
    """API-07: uma capacidade inexistente torna o plano infeasível."""
    corpo = {
        "task_id": "t2",
        "kind": "chat",
        "prompt": "Olá!",
        "max_tokens": 128,
        "required_capabilities": ["capacidade_impossivel"],
    }
    resposta = tasks(
        ApiRequest(method="POST", path="/tasks", body=json.dumps(corpo)),
        service=_servico_fixo(),
    )
    assert resposta.status == 200
    assert resposta.payload["selection"]["missing"] == ["capacidade_impossivel"]
    assert resposta.payload["plan"]["feasible"] is False
    assert resposta.payload["plan"]["model_id"] is None


def test_tasks_kind_invalido_devolve_400() -> None:
    """API-07: um ``kind`` desconhecido é rejeitado com 400."""
    corpo = {"task_id": "t3", "kind": "mágico", "prompt": "Olá!", "max_tokens": 128}
    resposta = tasks(ApiRequest(method="POST", path="/tasks", body=json.dumps(corpo)))
    assert resposta.status == 400
    assert "kind invalido" in resposta.payload["error"]


def test_tasks_body_mal_formado_devolve_400() -> None:
    """API-07: um corpo não-JSON é rejeitado com 400."""
    resposta = tasks(
        ApiRequest(method="POST", path="/tasks", body="isto não é JSON{")
    )
    assert resposta.status == 400
    assert "JSON" in resposta.payload["error"]


def test_tasks_endpoint_http_roundtrip(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(
        f"http://{host}:{port}", "/tasks", corpo=json.dumps(_corpo_tarefa_chat())
    )
    assert status == 200
    assert "task_id" in payload
    assert "classification" in payload
    assert "plan" in payload


def test_tasks_metodo_nao_suportado_devolve_405(
    gateway_http: tuple[StdLibHttpGateway, str, int],
) -> None:
    _, host, port = gateway_http
    status, payload = _requisicao(f"http://{host}:{port}", "/tasks", metodo="GET")
    assert status == 405
    assert payload == {"error": "metodo nao suportado nesta rota"}