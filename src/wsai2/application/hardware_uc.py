"""Serviço do use-case de perfil de hardware (APP-04).

Monta o ``HardwareProfileResponse`` a partir da superfície pública de
``wsai2.hardware`` (``discover_hardware``) — sem lógica central de
decisão: o serviço tipa o perfil estrutural produzido pelo domínio. A
fonte do perfil é injectável, permitindo testes deterministas.
"""

from __future__ import annotations

from typing import Callable

from wsai2.hardware import HardwareProfile, discover_hardware

from .contract import HardwareProfileRequest, HardwareProfileResponse

HardwareSource = Callable[[], HardwareProfile]


class HardwareProfileService:
    """Resolve o use-case de perfil de hardware (APP-04).

    Attributes:
        profile_source: fonte do perfil estrutural (Hardware Capability).
    """

    def __init__(self, profile_source: HardwareSource | None = None) -> None:
        self._profile_source = (
            profile_source if profile_source is not None else discover_hardware
        )

    def resolve(self, request: HardwareProfileRequest) -> HardwareProfileResponse:
        """Devolve a resposta do use-case com o perfil estrutural actual."""
        return HardwareProfileResponse(profile=self._profile_source())