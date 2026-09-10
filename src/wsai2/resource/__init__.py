"""Subsistema de Governação de Recursos do WorkStation AI 2.

Responsável pela governação de recursos (hardening 05 do
CORE_HARDENING_PLAN): normalizar limites declarativos, validar folga
efectiva contra os perfis de hardware e runtime e contabilizar
alocações/reservas ao longo de execuções.

Desde o KERNEL-09, este pacote é **apenas a fronteira** (shell de
re-export): a superfície sancionada mantém-se aqui, mas a implementação
pesada (tipos de contrato e o ``ResourceGovernor``) desceu para
`wsai2.infrastructure`, por trás deste contrato público.
"""

from wsai2.infrastructure.base_resource import (
    AllocationState,
    ResourceAllocation,
    ResourceBudgetResult,
    ResourceCheck,
    ResourceDimension,
    ResourceVerdict,
)
from wsai2.infrastructure.governor import ResourceGovernor

# Contrato público da fronteira de recursos (KERNEL-05): a superfície
# sancionada é o `__all__` abaixo, congelada por teste de contrato.
RESOURCE_CONTRACT_VERSION = "1.0"

__all__ = [
    "AllocationState",
    "ResourceAllocation",
    "ResourceBudgetResult",
    "ResourceCheck",
    "ResourceDimension",
    "ResourceGovernor",
    "ResourceVerdict",
]