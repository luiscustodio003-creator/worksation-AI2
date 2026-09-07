"""Subsistema Platform Foundation do WorkStation AI 2.

Responsável por abstrair as diferenças entre sistemas operativos e
fornecer acesso controlado a funcionalidades específicas de Windows e
Linux, isolando o código dependente do SO da lógica de domínio.

Daqui exporta-se a interface pública `get_platform()` destinada ao resto
da aplicação.
"""

from .base import OperatingSystem, PlatformName, PlatformProvider
from .factory import get_platform

__all__ = [
    "OperatingSystem",
    "PlatformName",
    "PlatformProvider",
    "get_platform",
]