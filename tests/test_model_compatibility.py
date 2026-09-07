"""Testes do subsistema Model Intelligence — compatibilidade.

Valida a avaliação de compatibilidade dos modelos contra o hardware, o
runtime e as capacidades requeridas: veredictos (disponível,
condicionado, indisponível), verificações por requisito e filtragem de
modelos compatíveis.
"""

from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.hardware import Architecture, CpuInfo, CpuVendor, GpuInfo, HardwareProfile, MemoryInfo, StorageInfo
from wsai2.model import (
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRequirements,
    ModelState,
    ModelVerdict,
    ModelCheck,
    compatible_models,
    create_default_registry,
    default_models,
    evaluate_model,
    evaluate_models,
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


def _modelo_teste(requirements: ModelRequirements) -> ModelDefinition:
    """Constrói uma definição de modelo de teste."""
    return ModelDefinition(
        id="modelo-teste",
        name="Modelo de Teste",
        description="Modelo para testes de compatibilidade.",
        kind=ModelKind.LLM,
        metadata=ModelMetadata(
            version="1",
            params_billions=1.0,
            context_window_tokens=2048,
        ),
        requirements=requirements,
    )


def test_modelo_disponivel() -> None:
    """Requisitos satisfeitos devem resultar em AVAILABLE."""
    models = create_default_registry()
    capabilities = create_capability_registry()
    definition = models.get("all-MiniLM-L6-v2")
    assert definition is not None

    verdict = evaluate_model(definition, _hardware(), _runtime(), capabilities)

    assert verdict.state is ModelState.AVAILABLE
    assert verdict.is_available is True
    assert verdict.missing_capabilities == ()


def test_modelo_condicionado_por_capacidade() -> None:
    """Capacidade requerida apenas condicionada deve resultar em RESTRICTED."""
    models = create_default_registry()
    capabilities = create_capability_registry()

    # local_llm_inference é RESTRICTED com apenas 6GB disponíveis
    verdict = evaluate_model(
        models.get("phi-3-mini"), _hardware(), _runtime(), capabilities
    )

    assert verdict.state is ModelState.RESTRICTED
    assert verdict.is_available is False
    assert verdict.missing_capabilities == ()


def test_modelos_disponiveis_com_runtime_folgado() -> None:
    """Com memória disponível suficiente, todos os modelos base ficam disponíveis."""
    models = create_default_registry()
    capabilities = create_capability_registry()

    verdicts = evaluate_models(models, _hardware(), _runtime(available_gb=16.0), capabilities)

    assert len(verdicts) == len(models)
    assert all(verdict.state is ModelState.AVAILABLE for verdict in verdicts)


def test_modelo_indisponivel_por_capacidade_faltante() -> None:
    """Capacidade estruturalmente indisponível deve resultar em UNAVAILABLE."""
    model = _modelo_teste(
        ModelRequirements(min_ram_gb=2.0, required_capabilities=("accelerated_ml",))
    )

    verdict = evaluate_model(model, _hardware(), _runtime(), create_capability_registry())

    assert verdict.state is ModelState.UNAVAILABLE
    assert verdict.missing_capabilities == ("accelerated_ml",)


def test_modelo_indisponivel_por_capacidade_nao_registada() -> None:
    """Capacidade requerida inexistente no registo deve tornar o modelo indisponível."""
    model = _modelo_teste(
        ModelRequirements(min_ram_gb=1.0, required_capabilities=("nao_existe",))
    )

    verdict = evaluate_model(model, _hardware(), _runtime(), create_capability_registry())

    assert verdict.state is ModelState.UNAVAILABLE
    assert verdict.missing_capabilities == ("nao_existe",)


def test_modelo_indisponivel_por_estrutura_gpu() -> None:
    """Modelo que exige GPU sem GPU no sistema deve ser UNAVAILABLE."""
    model = _modelo_teste(
        ModelRequirements(
            min_ram_gb=8.0,
            min_vram_gb=4.0,
            requires_gpu=True,
            min_cpu_cores=4,
            required_capabilities=("accelerated_ml",),
        )
    )

    # Sem capacidade acelerada
    verdict_sem_capacidade = evaluate_model(
        model, _hardware(), _runtime(), create_capability_registry()
    )
    assert verdict_sem_capacidade.state is ModelState.UNAVAILABLE

    # Sem GPU mesmo com a capacidade registada (capacidade acelerada indisponível)
    capabilities = create_capability_registry()
    model2 = _modelo_teste(
        ModelRequirements(min_ram_gb=8.0, min_vram_gb=4.0, requires_gpu=True)
    )
    verdict_sem_gpu = evaluate_model(model2, _hardware(), _runtime(), capabilities)
    assert verdict_sem_gpu.state is ModelState.UNAVAILABLE
    gpu_check = next((c for c in verdict_sem_gpu.checks if c.name == "gpu"), None)
    assert gpu_check is not None
    assert gpu_check.satisfied is False


def test_modelo_com_gpu_fica_disponivel() -> None:
    """Com GPU de VRAM suficiente, o modelo acelerado fica disponível."""
    capabilities = create_capability_registry()
    model = _modelo_teste(
        ModelRequirements(
            min_ram_gb=8.0,
            min_vram_gb=4.0,
            requires_gpu=True,
            min_cpu_cores=4,
            required_capabilities=("accelerated_ml",),
        )
    )

    verdict = evaluate_model(
        model,
        _hardware(vram_gb=8.0),
        _runtime(available_gb=12.0),
        capabilities,
    )

    assert verdict.state is ModelState.AVAILABLE


def test_avaliacao_models_cobre_todo_o_registo() -> None:
    """A avaliação do registo deve devolver um veredicto por definição."""
    models = create_default_registry()

    verdicts = evaluate_models(models, _hardware(), _runtime(), create_capability_registry())

    assert len(verdicts) == len(models)
    verdict_ids = {verdict.model_id for verdict in verdicts}
    assert verdict_ids == {model.id for model in default_models()}
    for verdict in verdicts:
        assert isinstance(verdict, ModelVerdict)
        assert verdict.state in ModelState


def test_models_compatibleis_filtram() -> None:
    """compatible_models apenas devolve modelos de facto disponíveis."""
    models = create_default_registry()

    # Com 6GB disponíveis, a inferência local está condicionada
    verdicts = compatible_models(models, _hardware(), _runtime(), create_capability_registry())

    available_ids = {verdict.model_id for verdict in verdicts}
    assert available_ids == {"all-MiniLM-L6-v2"}
    for verdict in verdicts:
        assert verdict.is_available is True


def test_verificacoes_por_requisito() -> None:
    """Os checks devem registar nome, valores e satisfação."""
    models = create_default_registry()
    definition = models.get("all-MiniLM-L6-v2")
    assert definition is not None

    verdict = evaluate_model(definition, _hardware(), _runtime(), create_capability_registry())

    check_names = {check.name for check in verdict.checks}
    assert "capabilities" in check_names
    assert "ram_total" in check_names
    assert "ram_available" in check_names
    assert "cpu_cores" in check_names
    assert "disk" in check_names

    for check in verdict.checks:
        assert isinstance(check, ModelCheck)
        assert check.satisfied is True


def test_verificacao_capacidades_registada_no_veredicto() -> None:
    """Falta de capacidade deve reflectir-se no check capabilities e em missing_capabilities."""
    model = _modelo_teste(
        ModelRequirements(min_ram_gb=1.0, required_capabilities=("accelerated_ml",))
    )

    verdict = evaluate_model(model, _hardware(), _runtime(), create_capability_registry())

    capabilities_check = next(
        (c for c in verdict.checks if c.name == "capabilities"), None
    )
    assert capabilities_check is not None
    assert capabilities_check.satisfied is False
    assert verdict.missing_capabilities == ("accelerated_ml",)


def test_summary_do_veredicto() -> None:
    """O resumo do veredicto deve conter o id e o estado."""
    models = create_default_registry()
    definition = models.get("all-MiniLM-L6-v2")
    assert definition is not None

    verdict = evaluate_model(definition, _hardware(), _runtime(), create_capability_registry())

    assert definition.id in verdict.summary