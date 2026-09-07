"""Fábrica de descoberta de runtime.

Selecciona a estratégia de descoberta adequada e agrega o perfil
completo de runtime (estado de execução actual do sistema) com a
análise derivada de disponibilidade efectiva.
"""

from __future__ import annotations

import time

import psutil

from .availability import _overall_status, analyze_runtime_availability
from .base import RuntimeDiscoverer, RuntimeProfile, SystemUptime
from .cpu import discover_cpu_load
from .memory import discover_memory_state
from .processes import discover_top_processes


def _discover_uptime() -> SystemUptime | None:
    """Descobre o tempo de actividade do sistema."""
    try:
        boot_ts = psutil.boot_time()
        uptime = time.time() - boot_ts
        return SystemUptime(
            boot_timestamp=boot_ts,
            uptime_seconds=uptime,
        )
    except Exception:
        return None


class _GenericRuntimeDiscoverer:
    """Descobridor genérico usando psutil (funciona em Windows e Linux)."""

    def discover_cpu_load(self):
        return discover_cpu_load()

    def discover_memory(self):
        return discover_memory_state()

    def discover_uptime(self):
        return _discover_uptime()

    def discover_all(self) -> RuntimeProfile:
        """Descobre e agrega todo o perfil de runtime com análise de disponibilidade."""
        cpu = self.discover_cpu_load()
        memory = self.discover_memory()
        processes = discover_top_processes(limit=10)
        uptime = self.discover_uptime()
        availability = analyze_runtime_availability(cpu, memory)
        return RuntimeProfile(
            cpu=cpu,
            memory=memory,
            processes=processes,
            uptime=uptime,
            availability=availability,
            overall_status=_overall_status(availability),
        )


def discover_runtime() -> RuntimeProfile:
    """Ponto de entrada público para descoberta de runtime.

    Devolve um :class:`RuntimeProfile` com o estado de execução
    actual do sistema: carga de CPU, utilização de memória,
    processos mais relevantes e tempo de actividade.
    """
    discoverer: RuntimeDiscoverer = _GenericRuntimeDiscoverer()
    return discoverer.discover_all()


__all__ = ["discover_runtime"]
