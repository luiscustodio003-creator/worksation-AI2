"""Testes da selecção de capacidades do Task Intelligence.

Valida a verificação das capacidades exigidas de uma tarefa contra o
Capability Engine, determinando a viabilidade da execução.
"""

from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.hardware import Architecture, CpuInfo, CpuVendor, GpuInfo, HardwareProfile, MemoryInfo, StorageInfo
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile, SystemUptime
from wsai2.task import (
    Task,
    TaskCapabilitySelection,
    TaskKind,
    requirements_for,
    select_capabilities,
)

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


def test_todas_as_capacidades_disponiveis() -> None:
    """Com todas as capacidades disponíveis, a tarefa é viável."""
    requisitos = requirements_for(
        Task(
            id="t-leve",
            kind=TaskKind.CHAT,
            prompt="Olá",
            required_capabilities=("lightweight_processing",),
        )
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(),
        _runtime(),
    )

    assert isinstance(selecao, TaskCapabilitySelection)
    assert selecao.required == ("lightweight_processing",)
    assert selecao.available == ("lightweight_processing",)
    assert selecao.missing == ()
    assert selecao.is_viable is True


def test_capacidade_em_falta_torna_inviavel() -> None:
    """Uma capacidade em falta deve tornar a tarefa inviável."""
    requisitos = requirements_for(
        Task(
            id="t-gpu",
            kind=TaskKind.EMBEDDING,
            prompt="Vectoriza",
            required_capabilities=("capacidade-inexistente",),
        )
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(),
        _runtime(),
    )

    assert selecao.missing == ("capacidade-inexistente",)
    assert selecao.available == ()
    assert selecao.is_viable is False
    assert "inviável" in selecao.summary


def test_gpu_ausente_marca_indisponivel() -> None:
    """Uma capacidade que exige GPU num sistema sem GPU é inviável."""
    requisitos = requirements_for(
        Task(
            id="t-acel",
            kind=TaskKind.EMBEDDING,
            prompt="Vectoriza",
            required_capabilities=("accelerated_ml",),
        )
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(vram_gb=None),
        _runtime(),
    )

    assert "accelerated_ml" in selecao.missing
    assert selecao.is_viable is False


def test_gpu_presente_permite_acelerada() -> None:
    """Num sistema com GPU suficiente, a capacidade acelerada está viável."""
    requisitos = requirements_for(
        Task(
            id="t-acel",
            kind=TaskKind.EMBEDDING,
            prompt="Vectoriza",
            required_capabilities=("accelerated_ml",),
        )
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(vram_gb=8.0),
        _runtime(available_gb=10.0),
    )

    assert selecao.available == ("accelerated_ml",)
    assert selecao.is_viable is True


def test_sem_capacidades_requeridas() -> None:
    """Uma tarefa sem capacidades exigidas é sempre viável."""
    requisitos = requirements_for(
        Task(id="t-simples", kind=TaskKind.CHAT, prompt="Olá")
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(),
        _runtime(),
    )

    assert selecao.required == ()
    assert selecao.available == ()
    assert selecao.missing == ()
    assert selecao.is_viable is True


def test_ordem_de_capacidades_preservada() -> None:
    """Disponíveis e em falta mantêm a ordem de declaração da tarefa."""
    requisitos = requirements_for(
        Task(
            id="t-misto",
            kind=TaskKind.CHAT,
            prompt="Olá",
            required_capabilities=(
                "accelerated_ml",
                "lightweight_processing",
                "inexistente-b",
            ),
        )
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(vram_gb=8.0),
        _runtime(available_gb=10.0),
    )

    assert selecao.available == ("accelerated_ml", "lightweight_processing")
    assert selecao.missing == ("inexistente-b",)
    assert selecao.summary.startswith("t-misto")


def test_tarefa_com_resumo_de_viabilidade() -> None:
    """O resumo deve indicar a contagem de capacidades disponíveis."""
    requisitos = requirements_for(
        Task(
            id="t-vi",
            kind=TaskKind.CHAT,
            prompt="Olá",
            required_capabilities=("lightweight_processing",),
        )
    )

    selecao = select_capabilities(
        requisitos,
        create_capability_registry(),
        _hardware(),
        _runtime(),
    )

    assert "1/1" in selecao.summary