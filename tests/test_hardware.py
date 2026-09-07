"""Testes do subsistema Hardware Intelligence.

Valida a descoberta de CPU, memória, GPU e armazenamento, a normalização
de dados, a agregação do perfil de hardware e as capacidades derivadas.
"""

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
    discover_gpus,
    discover_hardware,
    discover_storage,
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


def test_descobrir_gpu_retorna_lista() -> None:
    """A descoberta de GPU deve devolver uma lista (pode ser vazia)."""
    gpus = discover_gpus()
    assert isinstance(gpus, list)
    for gpu in gpus:
        assert isinstance(gpu, GpuInfo)
        assert isinstance(gpu.name, str)
        assert len(gpu.name) > 0
        assert isinstance(gpu.vendor, str)
        assert len(gpu.vendor) > 0
        if gpu.vram_bytes is not None:
            assert gpu.vram_bytes >= 0


def test_descobrir_storage_retorna_lista() -> None:
    """A descoberta de armazenamento deve devolver uma lista não vazia."""
    storage = discover_storage()
    assert isinstance(storage, list)
    assert len(storage) > 0  # Pelo menos a partição do sistema
    for disk in storage:
        assert isinstance(disk, StorageInfo)
        assert isinstance(disk.device_path, str)
        assert len(disk.device_path) > 0
        assert disk.total_bytes > 0
        assert disk.type in ("ssd", "hdd", "nvme", "usb", "unknown")
        if disk.mount_point:
            assert isinstance(disk.mount_point, str)


def test_perfil_hardware_agregado() -> None:
    """A fábrica deve agregar CPU, memória, GPU e storage num HardwareProfile coerente."""
    profile = discover_hardware()

    assert isinstance(profile, HardwareProfile)
    assert isinstance(profile.cpu, CpuInfo)
    assert isinstance(profile.memory, MemoryInfo)
    assert isinstance(profile.gpus, tuple)
    assert isinstance(profile.storage, tuple)
    # GPU pode ser vazio se não detectado, storage deve ter pelo menos 1
    assert len(profile.storage) > 0
    for gpu in profile.gpus:
        assert isinstance(gpu, GpuInfo)
    for disk in profile.storage:
        assert isinstance(disk, StorageInfo)


def test_perfil_hardware_tem_capacidades_derivadas() -> None:
    """O perfil deve incluir capacidades estruturais derivadas para cada domínio."""
    profile = discover_hardware()

    assert isinstance(profile.capabilities, tuple)
    assert len(profile.capabilities) == 4  # compute, memory, graphics, storage

    domains = {cap.domain for cap in profile.capabilities}
    expected_domains = {
        CapabilityDomain.COMPUTE,
        CapabilityDomain.MEMORY,
        CapabilityDomain.GRAPHICS,
        CapabilityDomain.STORAGE,
    }
    assert domains == expected_domains

    for cap in profile.capabilities:
        assert isinstance(cap, HardwareCapability)
        assert 0.0 <= cap.score <= 1.0
        assert isinstance(cap.level, CapabilityLevel)
        assert isinstance(cap.details, dict)


def test_perfil_hardware_nivel_global() -> None:
    """O perfil deve ter um nível global de capacidade válido."""
    profile = discover_hardware()

    assert isinstance(profile.overall_level, CapabilityLevel)


def test_capacidade_compute_valida() -> None:
    """A capacidade de computação deve ter detalhes relevantes."""
    profile = discover_hardware()
    cap = profile.compute_capability

    assert cap is not None
    assert cap.domain == CapabilityDomain.COMPUTE
    assert "physical_cores" in cap.details
    assert "logical_cores" in cap.details
    assert "architecture" in cap.details


def test_capacidade_memoria_valida() -> None:
    """A capacidade de memória deve ter detalhes relevantes."""
    profile = discover_hardware()
    cap = profile.memory_capability

    assert cap is not None
    assert cap.domain == CapabilityDomain.MEMORY
    assert "total_gb" in cap.details
    assert cap.details["total_gb"] > 0


def test_capacidade_graphics_valida() -> None:
    """A capacidade gráfica deve ter detalhes relevantes."""
    profile = discover_hardware()
    cap = profile.graphics_capability

    assert cap is not None
    assert cap.domain == CapabilityDomain.GRAPHICS
    assert "gpu_count" in cap.details
    assert "vendors" in cap.details


def test_capacidade_storage_valida() -> None:
    """A capacidade de armazenamento deve ter detalhes relevantes."""
    profile = discover_hardware()
    cap = profile.storage_capability

    assert cap is not None
    assert cap.domain == CapabilityDomain.STORAGE
    assert "device_count" in cap.details
    assert "total_gb" in cap.details
    assert cap.details["total_gb"] > 0


def test_resumos_textuais_nao_vazios() -> None:
    """Os resumos textuais devem ser strings não vazias."""
    profile = discover_hardware()
    assert isinstance(profile.cpu_summary, str)
    assert len(profile.cpu_summary) > 0
    assert isinstance(profile.memory_summary, str)
    assert len(profile.memory_summary) > 0
    assert isinstance(profile.gpu_summary, str)
    assert len(profile.gpu_summary) > 0
    assert isinstance(profile.storage_summary, str)
    assert len(profile.storage_summary) > 0


def test_cpu_vendor_known_values() -> None:
    """O vendor deve ser um dos valores conhecidos do enum."""
    cpu = discover_cpu()
    assert cpu.vendor in CpuVendor


def test_cpu_architecture_known_values() -> None:
    """A arquitectura deve ser um dos valores conhecidos do enum."""
    cpu = discover_cpu()
    assert cpu.architecture in Architecture


def test_capability_level_ordering() -> None:
    """Os níveis de capacidade devem ter ordem lógica."""
    levels = [
        CapabilityLevel.MINIMAL,
        CapabilityLevel.BASIC,
        CapabilityLevel.INTERMEDIATE,
        CapabilityLevel.ADVANCED,
        CapabilityLevel.HIGH_END,
    ]
    # Verificar que são todos valores únicos
    assert len(set(levels)) == len(levels)


def test_capability_domain_completo() -> None:
    """Todos os domínios de capacidade devem estar definidos."""
    domains = set(CapabilityDomain)
    expected = {
        CapabilityDomain.COMPUTE,
        CapabilityDomain.MEMORY,
        CapabilityDomain.GRAPHICS,
        CapabilityDomain.STORAGE,
    }
    assert domains == expected