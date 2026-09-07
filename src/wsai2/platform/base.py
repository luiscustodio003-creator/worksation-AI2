"""Definições fundamentais da camada de plataforma.

Este módulo contém apenas contratos e tipos — não implementa nenhuma
lógica específica de sistema operativo. Garante assim que o domínio
depende de uma abstração estável e não de detalhes concretos do SO.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol


class OperatingSystem(Enum):
    """Sistemas operativos suportados pela camada de plataforma."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


class PlatformName(Enum):
    """Nomes de plataforma normalizados para fins de apresentação."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PlatformInfo:
    """Descrição neutral de um sistema operativo detectado.

    Devolvida pela camada de plataforma a consumidores que não precisam
    de conhecer os detalhes concretos do SO subjacente.
    """

    os: OperatingSystem
    name: str
    release: str
    version: str
    machine: str

    @property
    def is_windows(self) -> bool:
        """Indica se a plataforma detectada é Windows."""
        return self.os is OperatingSystem.WINDOWS

    @property
    def is_linux(self) -> bool:
        """Indica se a plataforma detectada é Linux."""
        return self.os is OperatingSystem.LINUX


class PlatformProvider(Protocol):
    """Contrato que qualquer adaptador de plataforma deve cumprir.

    Cada adaptador (Windows, Linux, etc.) implementa este protocolo,
    permitindo que a lógica de domínio interaja com a plataforma de
    forma uniforme.
    """

    def detect(self) -> PlatformInfo:
        """Detecta e devolve a descrição da plataforma."""
        ...


def detect_operating_system() -> OperatingSystem:
    """Infere o sistema operativo corrente a partir do ambiente Python.

    Utiliza apenas o módulo padrão ``sys`` para evitar dependências
    externas e garantir portabilidade.
    """
    if sys.platform.startswith("win"):
        return OperatingSystem.WINDOWS
    if sys.platform.startswith("linux"):
        return OperatingSystem.LINUX
    if sys.platform.startswith("darwin"):
        return OperatingSystem.MACOS
    return OperatingSystem.UNKNOWN


def build_platform_info(os_name: OperatingSystem) -> PlatformInfo:
    """Constrói um :class:`PlatformInfo` a partir de dados do Python.

    Recolhe os detalhes neutros do sistema (nome, release, versão e
    arquitectura) usando o módulo padrão ``platform``.
    """
    return PlatformInfo(
        os=os_name,
        name=platform.system() or os_name.name.lower(),
        release=platform.release() or "unknown",
        version=platform.version() or "unknown",
        machine=platform.machine() or "unknown",
    )