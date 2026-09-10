"""Serviço do use-case de modelos (APP-07).

Monta o ``ModelsResponse`` a partir de ``wsai2.model``
(``evaluate_models``) e honra o filtro opcional por categoria
(``ModelsRequest.category``) usando a associação de categoria das
definições do registo (``category_for``) — a Application apenas compõe
factos de domínio, sem lógica de avaliação.
"""

from __future__ import annotations

from typing import Callable

from wsai2 import capability as _capability
from wsai2 import model as _model
from wsai2.hardware import HardwareProfile, discover_hardware
from wsai2.runtime import RuntimeProfile, discover_runtime

from .contract import ModelsRequest, ModelsResponse

ModelRegistrySource = Callable[[], _model.ModelRegistry]
CapabilityRegistrySource = Callable[[], _capability.CapabilityRegistry]
HardwareSource = Callable[[], HardwareProfile]
RuntimeSource = Callable[[], RuntimeProfile]


class ModelsService:
    """Resolve o use-case de avaliação de modelos (APP-07).

    Attributes:
        model_registry_source: fonte do registo de definições de modelo.
        capability_registry_source: fonte do registo de capacidades.
        hardware_source: fonte do perfil estrutural (Hardware Capability).
        runtime_source: fonte do estado momentâneo (Runtime State).
    """

    def __init__(
        self,
        model_registry_source: ModelRegistrySource | None = None,
        capability_registry_source: CapabilityRegistrySource | None = None,
        hardware_source: HardwareSource | None = None,
        runtime_source: RuntimeSource | None = None,
    ) -> None:
        self._model_registry_source = (
            model_registry_source
            if model_registry_source is not None
            else _model.create_default_registry
        )
        self._capability_registry_source = (
            capability_registry_source
            if capability_registry_source is not None
            else _capability.create_default_registry
        )
        self._hardware_source = (
            hardware_source if hardware_source is not None else discover_hardware
        )
        self._runtime_source = (
            runtime_source if runtime_source is not None else discover_runtime
        )

    def resolve(self, request: ModelsRequest) -> ModelsResponse:
        """Devolve os veredictos, filtrando por categoria quando pedido."""
        registo = self._model_registry_source()
        veredictos = _model.evaluate_models(
            registo,
            self._hardware_source(),
            self._runtime_source(),
            self._capability_registry_source(),
        )
        if request.category is not None:
            veredictos = tuple(
                veredicto
                for veredicto in veredictos
                if _model.category_for(registo.get(veredicto.model_id))
                is request.category
            )
        return ModelsResponse(verdicts=veredictos)