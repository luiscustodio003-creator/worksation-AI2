"""Subsistema Hardware Intelligence do WorkStation AI 2.

Responsável por descobrir e descrever CPU, memória, GPU, armazenamento
e características relevantes do sistema. O código específico de Windows
e Linux permanece isolado na camada de plataforma.

Daqui exporta-se a interface pública `discover_hardware()` destinada ao
resto da aplicação.
"""

from .base import (
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
from .factory import discover_hardware
from .gpu import discover_gpus
from .storage import discover_storage

__all__ = [
    "Architecture",
    "CapabilityDomain",
    "CapabilityLevel",
    "CpuInfo",
    "CpuVendor",
    "GpuInfo",
    "HardwareCapability",
    "HardwareProfile",
    "MemoryInfo",
    "StorageInfo",
    "discover_gpus",
    "discover_storage",
    "discover_hardware",
]