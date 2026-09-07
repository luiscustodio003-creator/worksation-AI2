"""Contratos e tipos fundamentais do Hardware Intelligence.

Este módulo contém apenas definições de tipos, enums e protocolos —
não implementa nenhuma lógica de descoberta concreta. Garante que o
domínio depende de contratos estáveis e não de detalhes de implementação.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Architecture(Enum):
    """Arquitecturas de CPU conhecidas."""

    X86_64 = "x86_64"
    ARM64 = "arm64"
    ARM = "arm"
    X86 = "x86"
    UNKNOWN = "unknown"


class CpuVendor(Enum):
    """Fabricantes de CPU conhecidos."""

    INTEL = "intel"
    AMD = "amd"
    ARM = "arm"
    QUALCOMM = "qualcomm"
    APPLE = "apple"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CpuInfo:
    """Descrição neutral de um processador.

    Contém apenas informação estrutural (capacidade de hardware), não
    estado de runtime como carga ou frequência actual.
    """

    vendor: CpuVendor
    model_name: str
    architecture: Architecture
    physical_cores: int
    logical_cores: int
    max_frequency_mhz: float | None = None
    cache_l1_kb: int | None = None
    cache_l2_kb: int | None = None
    cache_l3_kb: int | None = None
    features: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_hyperthreading(self) -> bool:
        """Indica se o CPU suporta hyperthreading/SMT."""
        return self.logical_cores > self.physical_cores


@dataclass(frozen=True)
class MemoryInfo:
    """Descrição neutral da memória do sistema.

    Contém capacidade estrutural (hardware capability), não estado de
    runtime como memória livre actual (isso pertence a Runtime Intelligence).
    """

    total_bytes: int
    swap_total_bytes: int = 0

    @property
    def total_gb(self) -> float:
        """Memória total em gigabytes."""
        return self.total_bytes / (1024 ** 3)

    @property
    def swap_total_gb(self) -> float:
        """Swap total em gigabytes."""
        return self.swap_total_bytes / (1024 ** 3)

    @property
    def has_swap(self) -> bool:
        """Indica se existe swap configurado."""
        return self.swap_total_bytes > 0


@dataclass(frozen=True)
class GpuInfo:
    """Descrição neutral de uma GPU (estrutura base para expansão futura)."""

    name: str
    vendor: str
    vram_bytes: int | None = None
    driver_version: str | None = None


@dataclass(frozen=True)
class StorageInfo:
    """Descrição neutral de um dispositivo de armazenamento (estrutura base)."""

    device_path: str
    total_bytes: int
    type: str  # "ssd", "hdd", "nvme", "unknown"
    mount_point: str | None = None


@dataclass(frozen=True)
class HardwareProfile:
    """Perfil completo de capacidades de hardware do sistema.

    Agrega toda a informação estrutural descoberta. Representa
    *Hardware Capability* (capacidade estrutural) — distinto de
    *Runtime State* (estado momentâneo de execução).
    """

    cpu: CpuInfo
    memory: MemoryInfo
    gpus: tuple[GpuInfo, ...] = field(default_factory=tuple)
    storage: tuple[StorageInfo, ...] = field(default_factory=tuple)

    @property
    def cpu_summary(self) -> str:
        """Resumo textual do CPU para apresentação."""
        ht = " + HT" if self.cpu.has_hyperthreading else ""
        return f"{self.cpu.vendor.value.upper()} {self.cpu.model_name} ({self.cpu.physical_cores}C/{self.cpu.logical_cores}T{ht})"

    @property
    def memory_summary(self) -> str:
        """Resumo textual da memória para apresentação."""
        swap = f" + {self.memory.swap_total_gb:.1f}GB swap" if self.memory.has_swap else ""
        return f"{self.memory.total_gb:.1f}GB RAM{swap}"


class HardwareDiscoverer(Protocol):
    """Protocolo para descoberta de hardware.

    Cada implementação concreta (Windows, Linux, genérica) deve
    cumprir este contrato.
    """

    def discover_cpu(self) -> CpuInfo:
        """Descobre informação do processador."""
        ...

    def discover_memory(self) -> MemoryInfo:
        """Descobre informação de memória."""
        ...

    def discover_gpus(self) -> tuple[GpuInfo, ...]:
        """Descobre GPUs (vazio na unidade inicial)."""
        ...

    def discover_storage(self) -> tuple[StorageInfo, ...]:
        """Descobre armazenamento (vazio na unidade inicial)."""
        ...

    def discover_all(self) -> HardwareProfile:
        """Descobre e agrega todo o perfil de hardware."""
        ...