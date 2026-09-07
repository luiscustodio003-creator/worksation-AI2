"""Subsistema Capability Engine do WorkStation AI 2.

Responsável por definir, registar e avaliar as capacidades reais que
o sistema consegue disponibilizar a partir de hardware, runtime,
software e fornecedores instalados.

Nesta unidade foram adicionadas a **avaliação** das capacidades contra
o HardwareProfile e o RuntimeProfile (veredictos disponível /
condicionada / indisponível com verificações por requisito). A
compatibilidade e o relatório de capacidades disponíveis fazem parte
das unidades seguintes da Fase 4.
"""

from .base import (
    CapabilityDefinition,
    CapabilityRequirements,
    CapabilityState,
    CapabilityVerdict,
    RequirementCheck,
)
from .evaluation import (
    available_capabilities,
    evaluate_capabilities,
    evaluate_capability,
)
from .registry import CapabilityRegistry, create_default_registry, default_capabilities

__all__ = [
    "CapabilityDefinition",
    "CapabilityRegistry",
    "CapabilityRequirements",
    "CapabilityState",
    "CapabilityVerdict",
    "RequirementCheck",
    "available_capabilities",
    "create_default_registry",
    "default_capabilities",
    "evaluate_capabilities",
    "evaluate_capability",
]