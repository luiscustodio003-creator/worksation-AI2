"""Fábrica da camada de plataforma.

Selecciona o adaptador adequado ao sistema operativo corrente e devolve-o
através da interface comum :class:`PlatformProvider`. O resto da aplicação
não deve construir adaptadores directamente.
"""

from __future__ import annotations

from .base import OperatingSystem, PlatformProvider, build_platform_info, detect_operating_system
from .linux import LinuxPlatformProvider
from .windows import WindowsPlatformProvider


class _FallbackPlatformProvider:
    """Adaptador genérico para sistemas operativos não suportados.

    Devolve uma descrição neutra sem dependências específicas de SO,
    garantindo que o sistema continua a funcionar de forma reduzida.
    """

    def detect(self):
        return build_platform_info(detect_operating_system())


def _provider_for(os_name: OperatingSystem) -> PlatformProvider:
    """Devolve o adaptador correspondente ao sistema operativo indicado.

    Sistemas desconhecidos (por exemplo macOS ou variantes não suportadas)
    obtêm um adaptador genérico neutro.
    """
    if os_name is OperatingSystem.WINDOWS:
        return WindowsPlatformProvider()
    if os_name is OperatingSystem.LINUX:
        return LinuxPlatformProvider()
    return _FallbackPlatformProvider()


def get_platform() -> PlatformProvider:
    """Devolve o adaptador de plataforma adequado ao SO corrente.

    Este é o ponto único de entrada pública para a camada de plataforma.
    """
    return _provider_for(detect_operating_system())


__all__ = ["get_platform"]