"""Subsistema de Governação de Recursos do WorkStation AI 2.

Responsável pela governação de recursos (hardening 05 do
CORE_HARDENING_PLAN): normalizar limites declarativos, validar folga
efectiva contra os perfis de hardware e runtime e contabilizar
alocações/reservas ao longo de execuções.

A medição estrutural (Hardware Capability) e a medição momentânea
(Runtime State) pertencem aos subsistemas ``wsai2.hardware`` e
``wsai2.runtime``; este subsistema reutiliza-as sem duplicar.
O agendamento (8.5) e o enforce de timeout/cancelamento (8.4) estão
fora do âmbito desta unidade.
"""

from .base import (
    AllocationState,
    ResourceAllocation,
    ResourceBudgetResult,
    ResourceCheck,
    ResourceDimension,
    ResourceVerdict,
)
from .governor import ResourceGovernor

__all__ = [
    "AllocationState",
    "ResourceAllocation",
    "ResourceBudgetResult",
    "ResourceCheck",
    "ResourceDimension",
    "ResourceGovernor",
    "ResourceVerdict",
]