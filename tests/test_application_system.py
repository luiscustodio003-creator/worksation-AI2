"""Testes do use-case System/Platform (APP-03).

Verifica que ``SystemInfoService`` monta o ``SystemInfoResponse`` a partir
das superfícies públicas de ``wsai2.platform`` e ``wsai2.runtime``, que as
fontes são injectáveis (determinismo em testes) e que a plataforma é
sempre tipada por ``PlatformInfo``.
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2.application import (
    SystemInfoRequest,
    SystemInfoResponse,
    SystemInfoService,
)
from wsai2.platform import (
    OperatingSystem,
    PlatformInfo,
    PlatformName,
)
from wsai2.runtime import SystemUptime


def _plataforma_fixa() -> PlatformInfo:
    return PlatformInfo(
        os=OperatingSystem.WINDOWS,
        name=PlatformName.WINDOWS.value,
        release="10",
        version="10.0.19045",
        machine="x86_64",
    )


class _ProviderFixo:
    def detect(self) -> PlatformInfo:
        return _plataforma_fixa()


def _uptime_fixo() -> SystemUptime:
    return SystemUptime(boot_timestamp=1000.0, uptime_seconds=3600.0)


def test_resolve_padrao_devolve_plataforma_do_sistema() -> None:
    """APP-03: por omissão, o serviço usa o adaptador real da plataforma."""
    servico = SystemInfoService()
    resposta = servico.resolve(SystemInfoRequest())
    assert isinstance(resposta, SystemInfoResponse)
    assert isinstance(resposta.platform, PlatformInfo)
    assert resposta.platform.os in OperatingSystem
    assert resposta.platform.name


def test_resolve_com_provider_injectado() -> None:
    """APP-03: um provider fixo controla a plataforma devolvida."""
    servico = SystemInfoService(provider=_ProviderFixo())
    resposta = servico.resolve(SystemInfoRequest())
    assert resposta.platform == _plataforma_fixa()
    assert resposta.platform.is_windows


def test_resolve_com_uptime_injectado() -> None:
    """APP-03: a fonte de uptime é injectável e tipada por ``SystemUptime``."""
    servico = SystemInfoService(
        provider=_ProviderFixo(), uptime_source=lambda: _uptime_fixo()
    )
    resposta = servico.resolve(SystemInfoRequest())
    assert isinstance(resposta.uptime, SystemUptime)
    assert resposta.uptime.uptime_seconds == 3600.0


def test_resolve_uptime_padrao_provem_do_runtime() -> None:
    """APP-03: sem fonte injectada, o uptime vem do ``discover_runtime``."""
    servico = SystemInfoService(provider=_ProviderFixo())
    resposta = servico.resolve(SystemInfoRequest())
    assert resposta.uptime is None or isinstance(resposta.uptime, SystemUptime)


def test_resposta_e_imutavel_e_igual_ao_contrato() -> None:
    """APP-03: a resposta respeita o contrato congelado (frozen dataclass)."""
    servico = SystemInfoService(
        provider=_ProviderFixo(), uptime_source=lambda: _uptime_fixo()
    )
    resposta = servico.resolve(SystemInfoRequest())

    esperada = SystemInfoResponse(platform=_plataforma_fixa(), uptime=_uptime_fixo())
    assert resposta == esperada

    with pytest.raises(FrozenInstanceError):
        resposta.platform = _plataforma_fixa()