"""Fábrica de descoberta de hardware.

Selecciona a estratégia de descoberta adequada e agrega o perfil completo
de hardware com capacidades estruturais derivadas.
"""

from __future__ import annotations

from .base import HardwareDiscoverer, HardwareProfile
from .cpu import discover_cpu
from .memory import discover_memory
from .gpu import discover_gpus
from .storage import discover_storage
from .profile import analyze_hardware_profile


class _GenericHardwareDiscoverer:
    """Descobridor genérico usando psutil (funciona em Windows e Linux)."""

    def discover_cpu(self):
        return discover_cpu()

    def discover_memory(self):
        return discover_memory()

    def discover_gpus(self):
        return tuple(discover_gpus())

    def discover_storage(self):
        return tuple(discover_storage())

    def discover_all(self) -> HardwareProfile:
        """Descobre e agrega todo o perfil de hardware com análise de capacidades."""
        cpu = self.discover_cpu()
        memory = self.discover_memory()
        gpus = self.discover_gpus()
        storage = self.discover_storage()
        return analyze_hardware_profile(cpu, memory, gpus, storage)


def discover_hardware() -> HardwareProfile:
    """Ponto de entrada público para descoberta de hardware.

    Devolve um :class:`HardwareProfile` com as capacidades estruturais
    do sistema (CPU, memória, GPUs, armazenamento) e capacidades derivadas.
    """
    discoverer: HardwareDiscoverer = _GenericHardwareDiscoverer()
    return discoverer.discover_all()


__all__ = ["discover_hardware"]