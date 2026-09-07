"""Adaptador de plataforma dedicado ao sistema operativo Linux.

Contém código específico do Linux, isolado da lógica de domínio e das
infraestruturas de outros sistemas operativos. Nenhum outro módulo deve
importar este adaptador directamente: o acesso deve ocorrer através do
módulo ``wsai2.platform`` e da fábrica correspondente.
"""

from __future__ import annotations

from .base import (
    OperatingSystem,
    PlatformInfo,
    PlatformProvider,
    build_platform_info,
)


class LinuxPlatformProvider:
    """Adaptador Linux da camada de plataforma.

    Cumpre o protocolo :class:`PlatformProvider`. Este adaptador apenas
    entra em funcionamento quando o sistema subjacente é Linux.
    """

    def detect(self) -> PlatformInfo:
        """Detecta e descreve a plataforma Linux corrente."""
        return build_platform_info(OperatingSystem.LINUX)