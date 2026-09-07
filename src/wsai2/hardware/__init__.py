"""Subsistema Hardware Intelligence do WorkStation AI 2.

Responsável por descobrir e descrever CPU, memória, GPU, armazenamento
e características relevantes do sistema. O código específico de Windows
e Linux permanece isolado na camada de plataforma.

Daqui exporta-se a interface pública `discover_hardware()` destinada ao
resto da aplicação.
"""

from .base import (
    Architecture,
    CpuInfo,
    CpuVendor,
    HardwareProfile,
    MemoryInfo,
)
from .factory import discover_hardware

__all__ = [
    "Architecture",
    "CpuInfo",
    "CpuVendor",
    "HardwareProfile",
    "MemoryInfo",
    "discover_hardware",
]