"""Testes do subsistema Capability Engine — avaliação de capacidades.

Valida a avaliação de capacidades contra perfis de hardware e runtime:
veredictos (disponível, condicionada, indisponível), verificações por
requisito e filtragem de capacidades disponíveis.
"""

from wsai2.capability import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRequirements,
    CapabilityState,
    CapabilityVerdict,
    RequirementCheck,
    available_capabilities,
    create_default_registry,
    default_capabilities,
    evaluate_capabilities,
    evaluate_capability,
)
from wsai2.hardware import Architecture, CpuInfo, CpuVendor, GpuInfo, HardwareProfile, MemoryInfo, StorageInfo
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


def _definition(
    capability_id: str,
    requirements: CapabilityRequirements,
) -> CapabilityDefinition:
    """Constrói uma definição de capacidade de teste."""
    return CapabilityDefinition(
        id=capability_id,
        name=f"Capacidade {capability_id}",
        description="Capacidade para testes de avaliação.",
        requirements=requirements,
    )


def test_avaliacao_capacidade_disponivel() -> None:
    """Requisitos satisfeitos devem resultar em AVAILABLE."""
    definition = _definition("teste", CapabilityRequirements(min_ram_gb=4.0, min_cpu_cores=2))

    verdict = evaluate_capability(definition, _hardware(), _runtime())

    assert verdict.state == CapabilityState.AVAILABLE
    assert verdict.is_available is True
    assert len(verdict.checks) >= 4


def test_avaliacao_indisponivel_por_estrutura() -> None:
    """Falha de requisito estrutural deve resultar em UNAVAILABLE."""
    # GPU obrigatória, mas o sistema de teste não tem GPU
    definition = _definition(
        "acelerado",
        CapabilityRequirements(min_ram_gb=8.0, min_vram_gb=4.0, requires_gpu=True, min_cpu_cores=4),
    )

    verdict = evaluate_capability(definition, _hardware(), _runtime(available_gb=12.0))

    assert verdict.state == CapabilityState.UNAVAILABLE
    assert verdict.is_available is False


def test_avaliacao_condicionada_por_runtime() -> None:
    """Falha de requisito de runtime deve resultar em RESTRICTED."""
    # RAM total suficiente (16GB) mas disponível insuficiente (6GB < 8GB)
    definition = _definition("inferencia", CapabilityRequirements(min_ram_gb=8.0, min_cpu_cores=4))

    verdict = evaluate_capability(definition, _hardware(), _runtime(available_gb=6.0))

    assert verdict.state == CapabilityState.RESTRICTED
    assert verdict.is_available is False


def test_avaliacao_estrutura_mais_runtime() -> None:
    """RAM estrutural insuficiente deve ser UNAVAILABLE mesmo com runtime folgado."""
    definition = _definition("pesado", CapabilityRequirements(min_ram_gb=64.0, min_cpu_cores=8))

    verdict = evaluate_capability(definition, _hardware(ram_gb=16.0), _runtime(available_gb=12.0))

    assert verdict.state == CapabilityState.UNAVAILABLE


def test_verificacoes_por_requisito() -> None:
    """Os checks devem registar nome, valores e satisfação."""
    definition = _definition("teste", CapabilityRequirements(min_ram_gb=4.0, min_cpu_cores=2))

    verdict = evaluate_capability(definition, _hardware(), _runtime())

    check_names = {check.name for check in verdict.checks}
    assert "ram_total" in check_names
    assert "ram_available" in check_names
    assert "cpu_cores" in check_names
    assert "disk" in check_names

    for check in verdict.checks:
        assert isinstance(check, RequirementCheck)
        assert check.satisfied is True


def test_verificacao_gpu_apresentada_quando_exigida() -> None:
    """Quando há exigência de GPU, deve existir um check gpu."""
    definition = _definition(
        "acelerado",
        CapabilityRequirements(min_ram_gb=8.0, min_vram_gb=4.0, requires_gpu=True, min_cpu_cores=4),
    )

    verdict = evaluate_capability(definition, _hardware(), _runtime())

    gpu_check = next((c for c in verdict.checks if c.name == "gpu"), None)
    assert gpu_check is not None
    assert gpu_check.satisfied is False  # teste sem GPU


def test_avaliacao_com_gpu_suficiente() -> None:
    """Com GPU de VRAM suficiente, a capacidade acelerada fica disponível."""
    definition = _definition(
        "acelerado",
        CapabilityRequirements(min_ram_gb=8.0, min_vram_gb=4.0, requires_gpu=True, min_cpu_cores=4),
    )

    verdict = evaluate_capability(
        definition,
        _hardware(vram_gb=8.0),
        _runtime(available_gb=12.0),
    )

    assert verdict.state == CapabilityState.AVAILABLE


def test_avaliacao_with_gpu_vram_insuficiente() -> None:
    """GPU presente mas com VRAM inferior ao mínimo deve ser UNAVAILABLE."""
    definition = _definition(
        "acelerado",
        CapabilityRequirements(min_ram_gb=8.0, min_vram_gb=4.0, requires_gpu=True, min_cpu_cores=4),
    )

    verdict = evaluate_capability(
        definition,
        _hardware(vram_gb=2.0),
        _runtime(available_gb=12.0),
    )

    assert verdict.state == CapabilityState.UNAVAILABLE


def test_avaliacao_capacidades_registo() -> None:
    """A avaliação do registo deve devolver um veredicto por definição."""
    registry = create_default_registry()

    verdicts = evaluate_capabilities(registry, _hardware(), _runtime())

    assert len(verdicts) == len(registry)
    verdict_ids = {verdict.capability_id for verdict in verdicts}
    expected_ids = {definition.id for definition in default_capabilities()}
    assert verdict_ids == expected_ids
    for verdict in verdicts:
        assert isinstance(verdict, CapabilityVerdict)
        assert verdict.state in CapabilityState


def test_capacidades_disponiveis_filtra() -> None:
    """available_capabilities apenas devolve capacidades de facto disponíveis."""
    registry = create_default_registry()
    runtime = _runtime(available_gb=1.0)

    verdicts = available_capabilities(registry, _hardware(), runtime)

    for verdict in verdicts:
        assert verdict.is_available is True
        assert verdict.state == CapabilityState.AVAILABLE

    # Com apenas 1GB de RAM disponível e sem GPU, só a capacidade leve
    # (min_ram 1GB, sem requisito de GPU) fica disponível.
    available_ids = {verdict.capability_id for verdict in verdicts}
    assert available_ids == {"lightweight_processing"}