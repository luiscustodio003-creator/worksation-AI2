"""Fábrica de descoberta de hardware.

Selecciona a estratégia de descoberta adequada e agrega o perfil completo
de hardware. Na unidade inicial, usa implementação genérica baseada em
psutil que funciona em Windows e Linux.
"""

from __future__ import annotations

from .base import HardwareDiscoverer, HardwareProfile
from .cpu import discover_cpu
from .memory import discover_memory


class _GenericHardwareDiscoverer:
    """Descobridor genérico usando psutil (funciona em Windows e Linux)."""

    def discover_cpu(self):
        return discover_cpu()

    def discover_memory(self):
        return discover_memory()

    def discover_gpus(self):
        # Unidade inicial: GPU vazio
        return ()

    def discover_storage(self):
        # Unidade inicial: storage vazio
        return ()

    def discover_all(self) -> HardwareProfile:
        """Descobre e agrega todo o perfil de hardware."""
        return HardwareProfile(
            cpu=self.discover_cpu(),
            memory=self.discover_memory(),
            gpus=self.discover_gpus(),
            storage=self.discover_storage(),
        )


def discover_hardware() -> HardwareProfile:
    """Ponto de entrada público para descoberta de hardware.

    Devolve um :class:`HardwareProfile` com as capacidades estruturais
    do sistema (CPU, memória, GPUs, armazenamento).
    """
    discoverer: HardwareDiscoverer = _GenericHardwareDiscoverer()
    return discoverer.discover_all()


__all__ = ["discover_hardware"]