"""Subsistema Runtime Intelligence do WorkStation AI 2.

Responsável por descrever o estado actual dos recursos: memória disponível,
carga de CPU/GPU, processos e disponibilidade efectiva. O código específico
de Windows e Linux permanece isolado na camada de plataforma.

Daqui exporta-se a interface pública `discover_runtime()` destinada ao
resto da aplicação.

O Runtime Intelligence representa *Runtime State* — distinto de
*Hardware Capability* (capacidade estrutural do subsistema 3.2).
"""

from .base import (
    CpuLoad,
    MemoryRuntime,
    ProcessInfo,
    RuntimeProfile,
    SystemUptime,
)
from .factory import discover_runtime

__all__ = [
    "CpuLoad",
    "MemoryRuntime",
    "ProcessInfo",
    "RuntimeProfile",
    "SystemUptime",
    "discover_runtime",
]
