"""Testes do subsistema Model Intelligence — recomendação.

Valida a política de recomendação: filtragem por categoria, exclusão de
modelos indisponíveis, ordenação por score/parâmetros/RAM, justificação
e alternativas.
"""

from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.hardware import Architecture, CpuInfo, CpuVendor, GpuInfo, HardwareProfile, MemoryInfo, StorageInfo
from wsai2.model import (
    ModelCategory,
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRecommendation,
    ModelRegistry,
    ModelRequirements,
    ModelState,
    create_default_registry,
    recommend_model,
)
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile

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
    )


def _modelo_custom(
    capability_id: str,
    requisitos: ModelRequirements,
    params: float = 1.0,
    category=None,
) -> ModelDefinition:
    """Constrói um modelo de teste com metadados configuráveis."""
    return ModelDefinition(
        id=capability_id,
        name=f"Modelo {capability_id}",
        description="Modelo para testes de recomendação.",
        kind=ModelKind.LLM,
        metadata=ModelMetadata(
            version="1",
            params_billions=params,
            context_window_tokens=2048,
        ),
        requirements=requisitos,
        category=category,
    )


def test_recomendacao_sem_filtro_com_runtime_folgado() -> None:
    """Com tudo disponível, o modelo mais capaz (mais parâmetros) deve vencer."""
    modelos = create_default_registry()

    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(available_gb=16.0),
        create_capability_registry(),
    )

    assert recomendacao is not None
    assert isinstance(recomendacao, ModelRecommendation)
    assert recomendacao.model_id == "qwen2.5-7b-instruct"
    assert recomendacao.score == 1.0
    assert recomendacao.state is ModelState.AVAILABLE
    assert recomendacao.is_suitable is True


def test_recomendacao_por_categoria() -> None:
    """Filtrar por categoria embeddings deve recomendar o modelo dessa categoria."""
    modelos = create_default_registry()

    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(),
        create_capability_registry(),
        category=ModelCategory.EMBEDDING,
    )

    assert recomendacao is not None
    assert recomendacao.model_id == "all-MiniLM-L6-v2"
    assert recomendacao.category is ModelCategory.EMBEDDING


def test_recomendacao_por_categoria_prioriza_disponivel() -> None:
    """Na categoria chat, o melhor disponível/condicionado deve ser escolhido."""
    modelos = create_default_registry()

    # Com 6GB, ambos os LLM estão condicionados (local_llm_inference RESTRICTED)
    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(),
        create_capability_registry(),
        category=ModelCategory.CHAT,
    )

    assert recomendacao is not None
    # Empate no score (0.5) → mais parâmetros primeiro → qwen
    assert recomendacao.model_id == "qwen2.5-7b-instruct"
    assert recomendacao.score == 0.5
    assert recomendacao.state is ModelState.RESTRICTED
    assert recomendacao.is_suitable is False


def test_recomendacao_com_alternativas() -> None:
    """A recomendação deve incluir alternativas ordenadas sem o escolhido."""
    modelos = create_default_registry()

    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(),
        create_capability_registry(),
    )

    assert recomendacao is not None
    assert recomendacao.model_id not in recomendacao.alternatives
    assert len(recomendacao.alternatives) >= 2


def test_recomendacao_categoria_sem_candidatos() -> None:
    """Categoria sem candidatos deve devolver None."""
    modelos = create_default_registry()

    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(),
        create_capability_registry(),
        category=ModelCategory.COMPLETION,
    )

    assert recomendacao is None


def test_recomendacao_ignora_indisponiveis() -> None:
    """Modelos indisponíveis (score 0) nunca devem ser recomendados."""
    apenas_gpu = ModelRegistry(
        (
            _modelo_custom(
                "gpu-obrigatoria",
                ModelRequirements(
                    min_vram_gb=4.0,
                    requires_gpu=True,
                    required_capabilities=("accelerated_ml",),
                ),
                params=10.0,
            ),
        )
    )

    # Sem GPU no sistema → modelo indisponível → sem candidatos
    recomendacao = recommend_model(
        apenas_gpu,
        _hardware(),
        _runtime(),
        create_capability_registry(),
    )

    assert recomendacao is None


def test_recomendacao_devolve_disponivel_quando_existe() -> None:
    """Com um modelo disponível, o indisponível/condicionado é preterido."""
    registo = ModelRegistry(
        (
            _modelo_custom(
                "gpu-obrigatoria",
                ModelRequirements(
                    min_vram_gb=4.0,
                    requires_gpu=True,
                    required_capabilities=("accelerated_ml",),
                ),
                params=50.0,
            ),
            _modelo_custom(
                "leve-disponivel",
                ModelRequirements(min_ram_gb=1.0, min_cpu_cores=1),
                params=1.0,
            ),
        )
    )

    recomendacao = recommend_model(
        registo,
        _hardware(),
        _runtime(),
        create_capability_registry(),
    )

    assert recomendacao is not None
    # O modelo leve (score 1.0) vence o acelerado (score 0.0, excluído)
    assert recomendacao.model_id == "leve-disponivel"
    assert recomendacao.score == 1.0


def test_recomendacao_summary_e_razao() -> None:
    """A recomendação deve ter resumo e justificação coerentes."""
    modelos = create_default_registry()

    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(),
        create_capability_registry(),
        category=ModelCategory.EMBEDDING,
    )

    assert recomendacao is not None
    assert "disponível" in recomendacao.reason
    assert recomendacao.name in recomendacao.summary


def test_recomendacao_registo_vazio() -> None:
    """Um registo vazio não deve produzir recomendação."""
    recomendacao = recommend_model(
        ModelRegistry(),
        _hardware(),
        _runtime(),
        create_capability_registry(),
    )

    assert recomendacao is None


def test_razao_condicionado_referida() -> None:
    """A justificação de um modelo condicionado deve explicar a limitação."""
    modelos = create_default_registry()

    recomendacao = recommend_model(
        modelos,
        _hardware(),
        _runtime(),
        create_capability_registry(),
        category=ModelCategory.CHAT,
    )

    assert recomendacao is not None
    assert "condicionado" in recomendacao.reason
    assert "insuficientes" in recomendacao.reason