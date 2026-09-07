"""Relatório de compatibilidade de capacidades contra o sistema.

Consolida a avaliação produzida pelo módulo ``evaluation`` num relatório
por capacidade — definição estrutural, veredicto e justificação textual
— e fecha o catálogo de capacidades disponíveis do roadmap da Fase 4.

A responsabilidade deste módulo é apenas *consolidar* informação já
produzida pelo Capability Engine: não decide estados nem repete lógica de
avaliação, que permanecem em ``evaluation``.
"""

from __future__ import annotations

from .base import CapabilityCompatibility, CompatibilityReport
from .evaluation import evaluate_capability
from .registry import CapabilityRegistry
from wsai2.hardware import HardwareProfile
from wsai2.runtime import RuntimeProfile


def build_compatibility(
    registry: CapabilityRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> CompatibilityReport:
    """Constrói o relatório consolidado de compatibilidade do sistema.

    Para cada definição do registo avalia a capacidade contra o
    hardware e o runtime actuais e associa o veredicto à definição,
    permitindo justificar cada estado e derivar o catálogo de
    capacidades disponíveis.
    """
    entries = tuple(
        CapabilityCompatibility(
            definition=definition,
            verdict=evaluate_capability(definition, hardware, runtime),
        )
        for definition in registry.all()
    )
    return CompatibilityReport(hardware=hardware, runtime=runtime, entries=entries)


__all__ = ["build_compatibility"]