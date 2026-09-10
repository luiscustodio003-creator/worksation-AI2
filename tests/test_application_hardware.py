"""Testes do use-case Hardware (APP-04).

Verifica que ``HardwareProfileService`` monta o ``HardwareProfileResponse``
a partir de ``discover_hardware`` (ou de uma fonte injectada) e tipa o
perfil estrutural por ``HardwareProfile`` — sem lógica de decisão.
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2.application import (
    HardwareProfileRequest,
    HardwareProfileResponse,
    HardwareProfileService,
)
from wsai2.hardware import HardwareProfile, discover_hardware


def _perfil_fixo() -> HardwareProfile:
    return discover_hardware()


def test_resolve_padrao_devolve_perfil_real() -> None:
    """APP-04: por omissão, o serviço usa a descoberta real de hardware."""
    servico = HardwareProfileService()
    resposta = servico.resolve(HardwareProfileRequest())
    assert isinstance(resposta, HardwareProfileResponse)
    assert isinstance(resposta.profile, HardwareProfile)
    assert resposta.profile.memory.total_bytes > 0


def test_resolve_com_fonte_injectada() -> None:
    """APP-04: uma fonte fixa controla o perfil devolvido."""
    perfil = _perfil_fixo()
    servico = HardwareProfileService(profile_source=lambda: perfil)
    resposta = servico.resolve(HardwareProfileRequest())
    assert resposta.profile is perfil
    assert resposta.profile.overall_level is perfil.overall_level


def test_resposta_tipa_capacidades_estruturais() -> None:
    """APP-04: a resposta expõe as capacidades estruturais do domínio."""
    servico = HardwareProfileService()
    resposta = servico.resolve(HardwareProfileRequest())
    assert len(resposta.profile.capabilities) > 0
    for capacidade in resposta.profile.capabilities:
        assert capacidade.score >= 0.0


def test_resposta_imutavel_a_contrato() -> None:
    """APP-04: a resposta respeita o contrato congelado (frozen dataclass)."""
    perfil = _perfil_fixo()
    servico = HardwareProfileService(profile_source=lambda: perfil)
    resposta = servico.resolve(HardwareProfileRequest())

    assert resposta == HardwareProfileResponse(profile=perfil)

    with pytest.raises(FrozenInstanceError):
        resposta.profile = perfil