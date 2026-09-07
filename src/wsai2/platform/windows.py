"""Adaptador de plataforma dedicado ao sistema operativo Windows.

Contém código específico do Windows, isolado da lógica de domínio e das
infraestruturas de outros sistemas operativos. Nenhum outro módulo deve
importar este adaptador: o acesso deve ocorrer através do módulo
``wsai2.platform`` e da fábrica correspondente.
"""

from __future__ import annotations

from .base import (
    OperatingSystem,
    PlatformInfo,
    PlatformProvider,
    build_platform_info,
)


class WindowsPlatformProvider:
    """Adaptador Windows da camada de plataforma.

    Cumpre o protocolo :class:`PlatformProvider`. Este adaptador
    apenas entra em funcionamento quando o sistema subjacente é Windows.
    """

    def detect(self) -> PlatformInfo:
        """Detecta e descreve a plataforma Windows corrente."""
        return build_platform_info(OperatingSystem.WINDOWS)