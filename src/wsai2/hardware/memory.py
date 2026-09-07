"""Descoberta de memória usando psutil com normalização cross-platform.

Este módulo isola a lógica de obtenção de informação de memória,
normalizando os dados brutos do psutil para os contratos definidos em
``base.py``. Representa *Hardware Capability* (capacidade estrutural),
não estado de runtime.
"""

from __future__ import annotations

import psutil

from .base import MemoryInfo


def discover_memory() -> MemoryInfo:
    """Descobre e devolve a informação normalizada de memória do sistema."""
    vmem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return MemoryInfo(
        total_bytes=vmem.total,
        swap_total_bytes=swap.total,
    )


__all__ = ["discover_memory"]