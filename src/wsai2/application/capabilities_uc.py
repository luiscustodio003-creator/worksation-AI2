"""Serviço do use-case de capacidades (APP-06).

Monta o ``CapabilitiesResponse`` a partir de ``wsai2.capability``
(``build_compatibility``) e honra o filtro opcional por domínio
(``CapabilitiesRequest.domain``) usando a associação de domínio nas
definições do registo — lógica de agrupamento mantida no módulo de
domínio (``CompatibilityReport.by_domain``), serviço apenas compõe.
"""

from __future__ import annotations

from typing import Callable

from wsai2.capability import (
    CapabilityRegistry,
    CompatibilityReport,
    build_compatibility,
    create_default_registry,
)
from wsai2.hardware import HardwareProfile, discover_hardware
from wsai2.runtime import RuntimeProfile, discover_runtime

from .contract import CapabilitiesRequest, CapabilitiesResponse

RegistrySource = Callable[[], CapabilityRegistry]
HardwareSource = Callable[[], HardwareProfile]
RuntimeSource = Callable[[], RuntimeProfile]


class CapabilitiesService:
    """Resolve o use-case de capacidades (APP-06).

    Attributes:
        registry_source: fonte do registo de definições de capacidade.
        hardware_source: fonte do perfil estrutural (Hardware Capability).
        runtime_source: fonte do estado momentâneo (Runtime State).
    """

    def __init__(
        self,
        registry_source: RegistrySource | None = None,
        hardware_source: HardwareSource | None = None,
        runtime_source: RuntimeSource | None = None,
    ) -> None:
        self._registry_source = (
            registry_source if registry_source is not None else create_default_registry
        )
        self._hardware_source = (
            hardware_source if hardware_source is not None else discover_hardware
        )
        self._runtime_source = (
            runtime_source if runtime_source is not None else discover_runtime
        )

    def resolve(self, request: CapabilitiesRequest) -> CapabilitiesResponse:
        """Devolve a resposta do use-case, filtrando por domínio quando pedido."""
        report = build_compatibility(
            self._registry_source(),
            self._hardware_source(),
            self._runtime_source(),
        )
        if request.domain is not None:
            report = CompatibilityReport(
                hardware=report.hardware,
                runtime=report.runtime,
                entries=report.by_domain(request.domain),
            )
        return CapabilitiesResponse(report=report)