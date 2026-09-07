"""Testes do subsistema Hardware Intelligence.

Valida a descoberta de CPU e memória, a normalização de dados e a
agregação do perfil de hardware.
"""

from wsai2.hardware import (
    Architecture,
    CpuInfo,
    CpuVendor,
    HardwareProfile,
    MemoryInfo,
    discover_hardware,
)
from wsai2.hardware.cpu import discover_cpu
from wsai2.hardware.memory import discover_memory


def test_descobrir_cpu_retorna_estrutura_valida() -> None:
    """A descoberta de CPU deve devolver CpuInfo com campos obrigatórios preenchidos."""
    cpu = discover_cpu()

    assert isinstance(cpu, CpuInfo)
    assert isinstance(cpu.vendor, CpuVendor)
    assert isinstance(cpu.architecture, Architecture)
    assert isinstance(cpu.model_name, str)
    assert len(cpu.model_name) > 0
    assert cpu.physical_cores >= 1
    assert cpu.logical_cores >= cpu.physical_cores
    assert isinstance(cpu.features, tuple)


def test_cpu_hyperthreading_detection() -> None:
    """A propriedade has_hyperthreading deve reflectir cores lógicos vs físicos."""
    cpu = discover_cpu()
    expected = cpu.logical_cores > cpu.physical_cores
    assert cpu.has_hyperthreading is expected


def test_descobrir_memoria_retorna_estrutura_valida() -> None:
    """A descoberta de memória deve devolver MemoryInfo com campos obrigatórios."""
    mem = discover_memory()

    assert isinstance(mem, MemoryInfo)
    assert mem.total_bytes > 0
    assert mem.total_gb > 0
    assert mem.swap_total_bytes >= 0
    assert mem.has_swap == (mem.swap_total_bytes > 0)


def test_perfil_hardware_agregado() -> None:
    """A fábrica deve agregar CPU e memória num HardwareProfile coerente."""
    profile = discover_hardware()

    assert isinstance(profile, HardwareProfile)
    assert isinstance(profile.cpu, CpuInfo)
    assert isinstance(profile.memory, MemoryInfo)
    assert isinstance(profile.gpus, tuple)
    assert isinstance(profile.storage, tuple)
    # GPU e storage vazios na unidade inicial
    assert len(profile.gpus) == 0
    assert len(profile.storage) == 0


def test_resumos_textuais_nao_vazios() -> None:
    """Os resumos textuais devem ser strings não vazias."""
    profile = discover_hardware()
    assert isinstance(profile.cpu_summary, str)
    assert len(profile.cpu_summary) > 0
    assert isinstance(profile.memory_summary, str)
    assert len(profile.memory_summary) > 0


def test_cpu_vendor_known_values() -> None:
    """O vendor deve ser um dos valores conhecidos do enum."""
    cpu = discover_cpu()
    assert cpu.vendor in CpuVendor


def test_cpu_architecture_known_values() -> None:
    """A arquitectura deve ser um dos valores conhecidos do enum."""
    cpu = discover_cpu()
    assert cpu.architecture in Architecture