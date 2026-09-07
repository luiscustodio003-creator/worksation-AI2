"""Testes do subsistema Capability Engine — relatório de compatibilidade.

Valida a construção do relatório consolidado por capacidade: estado
por capacidade, agrupamentos disponível/condicionada/indisponível,
justificação textual e coerência com a avaliação e o catálogo final de
capacidades disponíveis.
"""

from wsai2.capability import (
    CapabilityCompatibility,
    CapabilityState,
    CompatibilityReport,
    build_compatibility,
    available_capabilities,
    create_default_registry,
    default_capabilities,
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


def _estados_esperados() -> dict[str, CapabilityState]:
    """Estados esperados com o hardware/runtime padrão de teste."""
    return {
        "local_llm_inference": CapabilityState.RESTRICTED,
        "local_embeddings": CapabilityState.AVAILABLE,
        "accelerated_ml": CapabilityState.UNAVAILABLE,
        "lightweight_processing": CapabilityState.AVAILABLE,
    }


def test_reporte_tem_uma_entrada_por_capacidade() -> None:
    """O relatório deve ter uma entrada por definição registada."""
    registry = create_default_registry()

    report = build_compatibility(registry, _hardware(), _runtime())

    assert isinstance(report, CompatibilityReport)
    assert len(report.entries) == len(registry)
    assert len(report.entries) == len(default_capabilities())
    entry_ids = {entry.definition.id for entry in report.entries}
    assert entry_ids == {definition.id for definition in default_capabilities()}
    for entry in report.entries:
        assert isinstance(entry, CapabilityCompatibility)
        assert entry.state in CapabilityState


def test_reporte_estados_esperados() -> None:
    """Cada capacidade deve ter o estado esperado no cenário de teste."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    estados = {entry.definition.id: entry.state for entry in report.entries}
    assert estados == _estados_esperados()


def test_reporte_agrupamentos_por_estado() -> None:
    """Os agrupamentos disponível/condicionada/indisponível devem estar coerentes."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    assert {e.definition.id for e in report.available} == {
        "local_embeddings",
        "lightweight_processing",
    }
    assert {e.definition.id for e in report.restricted} == {"local_llm_inference"}
    assert {e.definition.id for e in report.unavailable} == {"accelerated_ml"}

    for entry in report.available:
        assert entry.is_available is True
    for entry in report.restricted + report.unavailable:
        assert entry.is_available is False


def test_reporte_coerente_com_available_capabilities() -> None:
    """O catálogo de disponíveis do relatório deve coincidir com a avaliação."""
    registry = create_default_registry()
    hardware = _hardware()
    runtime = _runtime()

    report = build_compatibility(registry, hardware, runtime)
    directos = available_capabilities(registry, hardware, runtime)

    assert {v.capability_id for v in directos} == {e.definition.id for e in report.available}


def test_justificacao_disponivel() -> None:
    """A justificação de uma capacidade disponível deve ser positiva."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    entry = next(
        entry for entry in report.entries if entry.definition.id == "local_embeddings"
    )
    assert entry.state is CapabilityState.AVAILABLE
    assert "todos os requisitos estão satisfeitos" in entry.justification


def test_justificacao_condicionada_por_runtime() -> None:
    """A justificação de uma capacidade condicionada deve indicar o requisito de runtime."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    entry = next(
        entry for entry in report.entries if entry.definition.id == "local_llm_inference"
    )
    assert entry.state is CapabilityState.RESTRICTED
    assert "condicionada no momento" in entry.justification
    assert "RAM disponível" in entry.justification


def test_justificacao_indisponivel_por_estrutura() -> None:
    """A justificação de uma capacidade indisponível deve indicar requisitos estruturais."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    entry = next(
        entry for entry in report.entries if entry.definition.id == "accelerated_ml"
    )
    assert entry.state is CapabilityState.UNAVAILABLE
    assert "Requisitos estruturais não satisfeitos" in entry.justification
    assert "GPU/VRAM" in entry.justification


def test_justificacao_referencia_valores() -> None:
    """A justificação deve referir os valores exigidos e disponíveis."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    entry = next(
        entry for entry in report.entries if entry.definition.id == "local_llm_inference"
    )
    assert "exigido 8.0" in entry.justification
    assert "disponível 6.0" in entry.justification


def test_reporte_com_recurso_suficiente() -> None:
    """Com memória disponível suficiente, apenas a falta de GPU condiciona."""
    report = build_compatibility(
        create_default_registry(),
        _hardware(),
        _runtime(available_gb=16.0),
    )

    assert {e.definition.id for e in report.available} == {
        "local_llm_inference",
        "local_embeddings",
        "lightweight_processing",
    }
    assert {e.definition.id for e in report.unavailable} == {"accelerated_ml"}


def test_reporte_considera_gpu_disponivel() -> None:
    """Com GPU de VRAM suficiente, a capacidade acelerada fica disponível."""
    report = build_compatibility(
        create_default_registry(),
        _hardware(vram_gb=8.0),
        _runtime(available_gb=12.0),
    )

    assert {e.definition.id for e in report.available} == {
        "local_llm_inference",
        "local_embeddings",
        "accelerated_ml",
        "lightweight_processing",
    }
    assert report.unavailable == ()


def test_reporte_summary_reflecte_contagens() -> None:
    """O resumo do relatório deve reflectir as contagens por estado."""
    report = build_compatibility(create_default_registry(), _hardware(), _runtime())

    assert "2 capacidades disponíveis" in report.summary
    assert "1 condicionadas" in report.summary
    assert "1 indisponíveis" in report.summary


def test_reporte_preserva_hardware_e_runtime() -> None:
    """O relatório deve preservar o hardware e o runtime que o originaram."""
    hardware = _hardware()
    runtime = _runtime()

    report = build_compatibility(create_default_registry(), hardware, runtime)

    assert report.hardware is hardware
    assert report.runtime is runtime