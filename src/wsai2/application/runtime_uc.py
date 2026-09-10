"""Serviço do use-case de estado de runtime (APP-05).

Monta o ``RuntimeProfileResponse`` a partir da superfície pública de
``wsai2.runtime`` (``discover_runtime``) — estado momentâneo dos recursos
(Runtime State), distinto da capacidade estrutural (Hardware Capability,
secção 4 da arquitectura). A fonte do perfil é injectável.
"""

from __future__ import annotations

from typing import Callable

from wsai2.runtime import RuntimeProfile, discover_runtime

from .contract import RuntimeProfileRequest, RuntimeProfileResponse

RuntimeSource = Callable[[], RuntimeProfile]


class RuntimeProfileService:
    """Resolve o use-case de estado de runtime (APP-05).

    Attributes:
        profile_source: fonte do perfil de runtime actual.
    """

    def __init__(self, profile_source: RuntimeSource | None = None) -> None:
        self._profile_source = (
            profile_source if profile_source is not None else discover_runtime
        )

    def resolve(self, request: RuntimeProfileRequest) -> RuntimeProfileResponse:
        """Devolve a resposta do use-case com o estado momentâneo."""
        return RuntimeProfileResponse(profile=self._profile_source())