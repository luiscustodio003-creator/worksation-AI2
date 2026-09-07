"""Subsistema Runtime Intelligence do WorkStation AI 2.

Responsável por descrever o estado actual dos recursos: memória disponível,
carga de CPU/GPU, processos e disponibilidade efectiva. O código específico
de Windows e Linux permanece isolado na camada de plataforma.

Daqui exporta-se a interface pública `discover_runtime()` destinada ao
resto da aplicação.

O Runtime Intelligence representa *Runtime State* — distinto de
*Hardware Capability* (capacidade estrutural do subsistema 3.2).
"""

from .availability import (
    analyze_runtime_availability,
)
from .base import (
    AvailabilityDomain,
    AvailabilityStatus,
    CpuLoad,
    MemoryRuntime,
    ProcessInfo,
    RuntimeAvailability,
    RuntimeProfile,
    SystemUptime,
)
from .factory import discover_runtime

__all__ = [
    "AvailabilityDomain",
    "AvailabilityStatus",
    "CpuLoad",
    "MemoryRuntime",
    "ProcessInfo",
    "RuntimeAvailability",
    "RuntimeProfile",
    "SystemUptime",
    "analyze_runtime_availability",
    "discover_runtime",
]
