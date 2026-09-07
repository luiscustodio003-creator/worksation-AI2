"""Descoberta de utilização de memória usando psutil cross-platform.

Este módulo isola a lógica de obtenção de estado de utilização de
memória, normalizando para os contratos definidos em ``base.py``.
Representa *Runtime State* — distinto de *Hardware Capability*
(capacidade estrutural descoberta por ``wsai2.hardware.memory``).
"""

from __future__ import annotations

import psutil

from .base import MemoryRuntime


def discover_memory_state() -> MemoryRuntime:
    """Descobre e devolve o estado de utilização actual de memória."""
    vmem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return MemoryRuntime(
        total_bytes=vmem.total,
        available_bytes=vmem.available,
        used_bytes=vmem.used,
        percent=vmem.percent,
        swap_total_bytes=swap.total,
        swap_used_bytes=swap.used,
        swap_percent=swap.percent,
    )


__all__ = ["discover_memory_state"]
