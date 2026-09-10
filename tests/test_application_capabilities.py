"""Testes do use-case Capabilities (APP-06).

Verifica que ``CapabilitiesService`` monta o ``CapabilitiesResponse`` a
partir de ``build_compatibility`` (fontes injectáveis) e honra o filtro
opcional por domínio (``CapabilitiesRequest.domain``) usando a associação
de domínio das definições do registo.
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2.application import (
    CapabilitiesRequest,
    CapabilitiesResponse,
    CapabilitiesService,
)
from wsai2.capability import CompatibilityReport, build_compatibility, create_default_registry
from wsai2.hardware import CapabilityDomain, discover_hardware
from wsai2.runtime import discover_runtime


def _resolver_padrao() -> CapabilitiesService:
    return CapabilitiesService()


def test_resolve_padrao_devolve_relatorio_real() -> None:
    """APP-06: por omissão, o serviço constrói o relatório do sistema."""
    servico = _resolver_padrao()
    resposta = servico.resolve(CapabilitiesRequest())
    assert isinstance(resposta, CapabilitiesResponse)
    assert isinstance(resposta.report, CompatibilityReport)
    assert len(resposta.report.entries) > 0
    assert len(resposta.report.available) > 0


def test_resolve_sem_dominio_carrega_todas_as_entradas() -> None:
    """APP-06: sem domínio, o relatório inclui entradas de todos os domínios."""
    resposta = _resolver_padrao().resolve(CapabilitiesRequest())
    dominios = {entry.definition.domain for entry in resposta.report.entries}
    assert CapabilityDomain.COMPUTE in dominios
    assert CapabilityDomain.GRAPHICS in dominios


def test_resolve_com_dominio_filtra_entradas() -> None:
    """APP-06: o filtro por domínio restringe as entradas do relatório."""
    pedido = CapabilitiesRequest(domain=CapabilityDomain.GRAPHICS)
    resposta = _resolver_padrao().resolve(pedido)
    assert len(resposta.report.entries) > 0
    for entry in resposta.report.entries:
        assert entry.definition.domain is CapabilityDomain.GRAPHICS


def test_resolve_com_fontes_injectadas() -> None:
    """APP-06: fontes fixas controlam o relatório devolvido."""
    hardware = discover_hardware()
    runtime = discover_runtime()
    servico = CapabilitiesService(
        hardware_source=lambda: hardware,
        runtime_source=lambda: runtime,
    )
    resposta = servico.resolve(CapabilitiesRequest())
    assert resposta.report.hardware is hardware
    assert resposta.report.runtime is runtime
    esperado = build_compatibility(create_default_registry(), hardware, runtime)
    assert resposta.report.entries == esperado.entries


def test_resposta_imutavel_a_contrato() -> None:
    """APP-06: a resposta respeita o contrato congelado (frozen dataclass)."""
    servico = _resolver_padrao()
    resposta = servico.resolve(CapabilitiesRequest())

    assert resposta == CapabilitiesResponse(report=resposta.report)

    with pytest.raises(FrozenInstanceError):
        resposta.report = CompatibilityReport(
            hardware=resposta.report.hardware,
            runtime=resposta.report.runtime,
        )