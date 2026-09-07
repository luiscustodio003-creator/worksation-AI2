"""Descoberta de carga do CPU usando psutil com normalização cross-platform.

Este módulo isola a lógica de obtenção de estado de utilização do
processador (carga, frequência), normalizando para os contratos
definidos em ``base.py``. Representa *Runtime State*, não
*Hardware Capability*.
"""

from __future__ import annotations

import psutil

from .base import CpuLoad


def _discover_per_core(interval: float = 0.1) -> tuple[float, ...]:
    """Obtém carga por core individual."""
    try:
        per = psutil.cpu_percent(interval=interval, percpu=True)
        return tuple(per)
    except Exception:
        return ()


def discover_cpu_load(interval: float = 0.1) -> CpuLoad:
    """Descobre e devolve o estado de carga actual do CPU.

    Args:
        interval: segundos de amostragem para ``cpu_percent``.
            Valores muito curtos podem dar leituras imprecisas.
    """
    percent = psutil.cpu_percent(interval=interval) or 0.0
    per_core = _discover_per_core(interval=0)
    count = psutil.cpu_count(logical=True) or 0

    # Frequência actual
    freq_current = None
    try:
        freq = psutil.cpu_freq()
        if freq and freq.current:
            freq_current = freq.current
    except Exception:
        pass

    return CpuLoad(
        percent=percent,
        per_core=per_core,
        count=count,
        frequency_current_mhz=freq_current,
    )


__all__ = ["discover_cpu_load"]
