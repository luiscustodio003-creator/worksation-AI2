"""Serviço do use-case de informação do sistema (APP-03).

Orquestra a montagem do ``SystemInfoResponse`` a partir das superfícies
públicas de ``wsai2.platform`` (plataforma) e ``wsai2.runtime`` (uptime),
sem lógica central de decisão: o serviço apenas recolhe e tipa os payloads
de domínio segundo os contratos definidos em ``contract.py``. As fontes
são injectáveis, permitindo testes deterministas e isolamento de SO.
"""

from __future__ import annotations

from typing import Callable

from wsai2.platform import PlatformInfo, PlatformProvider, get_platform
from wsai2.runtime import SystemUptime, discover_runtime

from .contract import SystemInfoRequest, SystemInfoResponse

UptimeSource = Callable[[], SystemUptime | None]


class SystemInfoService:
    """Resolve o use-case de informação do sistema (APP-03).

    Attributes:
        provider: adaptador de plataforma usado para detectar o sistema.
        uptime_source: fonte do uptime actual do sistema.
    """

    def __init__(
        self,
        provider: PlatformProvider | None = None,
        uptime_source: UptimeSource | None = None,
    ) -> None:
        self._provider = provider if provider is not None else get_platform()
        self._uptime_source = (
            uptime_source if uptime_source is not None else self._uptime_padrao
        )

    @staticmethod
    def _uptime_padrao() -> SystemUptime | None:
        return discover_runtime().uptime

    def resolve(self, request: SystemInfoRequest) -> SystemInfoResponse:
        """Devolve a resposta do use-case a partir das fontes de domínio."""
        plataforma = self._provider.detect()
        return SystemInfoResponse(platform=plataforma, uptime=self._uptime_source())