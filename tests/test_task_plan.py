"""Testes do plano de execução do Task Intelligence.

Valida o fecho do ciclo: requisitos → capacidades → modelo →
fornecedor saudável → passos, incluindo os caminhos de infeasibilidade.
"""

from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.hardware import Architecture, CpuInfo, CpuVendor, GpuInfo, HardwareProfile, MemoryInfo, StorageInfo
from wsai2.model import create_default_registry as create_model_registry
from wsai2.provider import ProviderDefinition, ProviderHealth, ProviderHealthStatus, ProviderRegistry, ProviderType
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile, SystemUptime
from wsai2.task import ExecutionPlan, Task, TaskKind, build_execution_plan

_GB = 1024 ** 3


def _hardware(
    ram_gb: float = 16.0,
    cores: int = 8,
    vram_gb: float | None = None,
    storage_gb: float = 500.0,
) -> HardwareProfile:
    """Constrói um HardwareProfile de teste."""
    gpus = ()
    if vram_gb:
        gpus = (
            GpuInfo(name="GPU Teste", vendor="nvidia", vram_bytes=int(vram_gb * _GB)),
        )
    return HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL,
            model_name="CPU de Teste",
            architecture=Architecture.X86_64,
            physical_cores=cores,
            logical_cores=cores * 2,
        ),
        memory=MemoryInfo(total_bytes=int(ram_gb * _GB)),
        gpus=gpus,
        storage=(
            StorageInfo(
                device_path="C:",
                total_bytes=int(storage_gb * _GB),
                type="ssd",
                mount_point="C:",
            ),
        ),
    )


def _runtime(ram_gb: float = 16.0, available_gb: float = 6.0) -> RuntimeProfile:
    """Constrói um RuntimeProfile de teste."""
    used = ram_gb - available_gb
    percent = (used / ram_gb) * 100.0 if ram_gb else 0.0
    return RuntimeProfile(
        cpu=CpuLoad(percent=30.0, per_core=(), count=8),
        memory=MemoryRuntime(
            total_bytes=int(ram_gb * _GB),
            available_bytes=int(available_gb * _GB),
            used_bytes=int(used * _GB),
            percent=percent,
        ),
        uptime=SystemUptime(boot_timestamp=0.0, uptime_seconds=3600.0),
    )


def _fornecedor_saudavel(
    capabilities: tuple[str, ...],
) -> tuple[ProviderHealth, ...]:
    """Constrói um health check saudável para um fornecedor local."""
    return (
        ProviderHealth(
            provider_id="ollama",
            name="Ollama",
            base_url="http://localhost:11434",
            status=ProviderHealthStatus.HEALTHY,
            model_count=1,
            capabilities_provided=capabilities,
        ),
    )


def test_plano_executavel_chat() -> None:
    """Uma tarefa de chat com tudo disponível deve ser executável."""
    plano = build_execution_plan(
        Task(id="t-chat", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        _fornecedor_saudavel(("local_llm_inference",)),
    )

    assert isinstance(plano, ExecutionPlan)
    assert plano.feasible is True
    assert plano.is_executable is True
    assert plano.model_id is not None
    assert plano.provider_id == "ollama"
    assert plano.category == "chat"
    assert plano.reasons == ()
    assert "executar via ollama" in plano.steps
    assert "t-chat" in plano.summary


def test_plano_embedding_executavel() -> None:
    """Uma tarefa de embedding deve escolher a categoria e o fornecedor."""
    plano = build_execution_plan(
        Task(
            id="t-emb",
            kind=TaskKind.EMBEDDING,
            prompt="Vectoriza",
            required_capabilities=("local_embeddings",),
        ),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        _fornecedor_saudavel(("local_llm_inference", "local_embeddings")),
    )

    assert plano.category == "embedding"
    assert plano.is_executable is True
    assert plano.model_id == "all-MiniLM-L6-v2"
    assert plano.provider_id == "ollama"


def test_plano_inviavel_por_capacidades() -> None:
    """Faltando capacidades, o plano deve ser inviável e justificado."""
    plano = build_execution_plan(
        Task(
            id="t-f",
            kind=TaskKind.EMBEDDING,
            prompt="Vectoriza",
            required_capabilities=("capacidade-inexistente",),
        ),
        create_capability_registry(),
        _hardware(),
        _runtime(),
        create_model_registry(),
        _fornecedor_saudavel(()),
    )

    assert plano.feasible is False
    assert plano.is_executable is False
    assert plano.model_id is None
    assert plano.provider_id is None
    assert any("capacidade" in reason for reason in plano.reasons)


def test_plano_inviavel_sem_fornecedor_saudavel() -> None:
    """Sem fornecedor saudável compatível, o plano não deve ser executável."""
    plano = build_execution_plan(
        Task(id="t-np", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        (),
    )

    assert plano.feasible is False
    assert plano.is_executable is False
    assert plano.model_id is not None
    assert plano.provider_id is None
    assert any("fornecedor" in reason for reason in plano.reasons)


def test_plano_ignora_fornecedor_sem_capacidades_do_modelo() -> None:
    """Um fornecedor saudável sem capacidades do modelo não deve ser escolhido."""
    plano = build_execution_plan(
        Task(id="t-sc", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        _fornecedor_saudavel(("local_embeddings",)),
    )

    assert plano.is_executable is False
    assert plano.provider_id is None


def test_plano_escolha_de_fornecedor_deterministica() -> None:
    """Com dois fornecedores saudáveis, deve escolher-se o primeiro por id."""
    saudaveis = (
        ProviderHealth(
            provider_id="alpha",
            name="Alpha",
            base_url="http://localhost:1",
            status=ProviderHealthStatus.HEALTHY,
            model_count=1,
            capabilities_provided=("local_llm_inference",),
        ),
        ProviderHealth(
            provider_id="beta",
            name="Beta",
            base_url="http://localhost:2",
            status=ProviderHealthStatus.HEALTHY,
            model_count=1,
            capabilities_provided=("local_llm_inference",),
        ),
    )

    plano = build_execution_plan(
        Task(id="t-2p", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        saudaveis,
    )

    assert plano.provider_id == "alpha"


def test_plano_degradado_nao_conta_como_saudavel() -> None:
    """Um fornecedor degradado não deve ser escolhido para o plano."""
    degradado = (
        ProviderHealth(
            provider_id="ollama",
            name="Ollama",
            base_url="http://localhost:11434",
            status=ProviderHealthStatus.DEGRADED,
            error="motor com problemas",
            capabilities_provided=("local_llm_inference",),
        ),
    )

    plano = build_execution_plan(
        Task(id="t-dg", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        degradado,
    )

    assert plano.is_executable is False
    assert plano.provider_id is None


def test_plano_de_baixo_custo_escolhe_modelo_adequado() -> None:
    """O plano respeita o limite de recursos: sem memória, sem modelo chat."""
    plano = build_execution_plan(
        Task(id="t-pobre", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(ram_gb=2.0, cores=1),
        _runtime(ram_gb=2.0, available_gb=1.0),
        create_model_registry(),
        _fornecedor_saudavel(("local_llm_inference",)),
    )

    assert plano.is_executable is False
    assert plano.model_id is None