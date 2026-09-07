"""Selecção de capacidades para uma tarefa.

Verifica, contra o **Capability Engine**, quais das capacidades exigidas
por uma tarefa estão realmente disponíveis no sistema, separando as
capacidades satisfeitas das que faltam e determinando se a tarefa é
executável.

Não avalia capacidades aqui: delega a avaliação ao Capability Engine
(estado real, distinguindo hardware capability de runtime state).
"""

from __future__ import annotations

from dataclasses import dataclass

from wsai2.capability import available_capabilities
from wsai2.capability import CapabilityRegistry
from wsai2.hardware import HardwareProfile
from wsai2.runtime import RuntimeProfile

from .requirements import TaskRequirements


@dataclass(frozen=True)
class TaskCapabilitySelection:
    """Resultado da selecção de capacidades para uma tarefa."""

    task_id: str
    required: tuple[str, ...]      # capacidades exigidas pela tarefa
    available: tuple[str, ...]     # capacidades satisfeitas pelo sistema
    missing: tuple[str, ...]       # capacidades em falta

    @property
    def is_viable(self) -> bool:
        """Indica se a tarefa é executável (nenhuma capacidade em falta)."""
        return not self.missing

    @property
    def summary(self) -> str:
        """Resumo textual da selecção para apresentação."""
        estado = "viável" if self.is_viable else "inviável"
        return f"{self.task_id} — {estado} ({len(self.available)}/{len(self.required)} capacidades)"


def select_capabilities(
    requirements: TaskRequirements,
    capability_registry: CapabilityRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> TaskCapabilitySelection:
    """Selecciona as capacidades disponíveis para a tarefa.

    As capacidades exigidas são verificadas contra os veredictos de
    disponibilidade do Capability Engine. A ordem de declaração é
    preservada; nada é inventado.
    """
    available_ids = {
        verdict.capability_id
        for verdict in available_capabilities(capability_registry, hardware, runtime)
    }

    available = tuple(
        capability_id
        for capability_id in requirements.required_capabilities
        if capability_id in available_ids
    )
    missing = tuple(
        capability_id
        for capability_id in requirements.required_capabilities
        if capability_id not in available_ids
    )
    return TaskCapabilitySelection(
        task_id=requirements.task_id,
        required=requirements.required_capabilities,
        available=available,
        missing=missing,
    )


__all__ = [
    "TaskCapabilitySelection",
    "select_capabilities",
]