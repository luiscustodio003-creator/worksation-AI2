"""Testes do use-case Runtime (APP-05).

Verifica que ``RuntimeProfileService`` monta o ``RuntimeProfileResponse``
a partir de ``discover_runtime`` (ou de uma fonte injectada) e tipa o
estado momentâneo por ``RuntimeProfile`` — preservando a separação
Hardware Capability vs Runtime State.
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2.application import (
    RuntimeProfileRequest,
    RuntimeProfileResponse,
    RuntimeProfileService,
)
from wsai2.runtime import RuntimeProfile, discover_runtime


def _perfil_fixo() -> RuntimeProfile:
    return discover_runtime()


def test_resolve_padrao_devolve_estado_real() -> None:
    """APP-05: por omissão, o serviço usa a descoberta real de runtime."""
    servico = RuntimeProfileService()
    resposta = servico.resolve(RuntimeProfileRequest())
    assert isinstance(resposta, RuntimeProfileResponse)
    assert isinstance(resposta.profile, RuntimeProfile)
    assert resposta.profile.cpu.percent >= 0.0


def test_resolve_com_fonte_injectada() -> None:
    """APP-05: uma fonte fixa controla o estado devolvido."""
    perfil = _perfil_fixo()
    servico = RuntimeProfileService(profile_source=lambda: perfil)
    resposta = servico.resolve(RuntimeProfileRequest())
    assert resposta.profile is perfil
    assert resposta.profile.overall_status is perfil.overall_status


def test_resposta_carrega_uptime_e_disponibilidade() -> None:
    """APP-05: uptime e disponibilidade do domínio são expostos."""
    servico = RuntimeProfileService()
    resposta = servico.resolve(RuntimeProfileRequest())
    assert resposta.profile.uptime is not None
    assert resposta.profile.uptime.uptime_seconds >= 0
    assert len(resposta.profile.availability) > 0


def test_resposta_imutavel_a_contrato() -> None:
    """APP-05: a resposta respeita o contrato congelado (frozen dataclass)."""
    perfil = _perfil_fixo()
    servico = RuntimeProfileService(profile_source=lambda: perfil)
    resposta = servico.resolve(RuntimeProfileRequest())

    assert resposta == RuntimeProfileResponse(profile=perfil)

    with pytest.raises(FrozenInstanceError):
        resposta.profile = perfil