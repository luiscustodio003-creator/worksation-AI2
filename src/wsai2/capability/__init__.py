"""Subsistema Capability Engine do WorkStation AI 2.

Responsável por definir, registar, avaliar e reportar as capacidades
reais que o sistema consegue disponibilizar a partir de hardware,
runtime, software e fornecedores instalados.

Nesta unidade foi adicionado o **relatório de compatibilidade**:
consolida a avaliação por capacidade (estado, requisitos e justificação
textual) e fecha o catálogo de capacidades disponíveis da Fase 4.
"""

from .base import (
    CapabilityCompatibility,
    CapabilityDefinition,
    CapabilityRequirements,
    CapabilityState,
    CapabilityVerdict,
    CompatibilityReport,
    RequirementCheck,
)
from .compatibility import build_compatibility
from .evaluation import (
    available_capabilities,
    evaluate_capabilities,
    evaluate_capability,
)
from .registry import CapabilityRegistry, create_default_registry, default_capabilities

__all__ = [
    "CapabilityCompatibility",
    "CapabilityDefinition",
    "CapabilityRegistry",
    "CapabilityRequirements",
    "CapabilityState",
    "CapabilityVerdict",
    "CompatibilityReport",
    "RequirementCheck",
    "available_capabilities",
    "build_compatibility",
    "create_default_registry",
    "default_capabilities",
    "evaluate_capabilities",
    "evaluate_capability",
]