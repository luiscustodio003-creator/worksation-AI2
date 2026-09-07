"""Contratos e tipos fundamentais do Capability Engine.

Este módulo contém apenas definições de tipos e dataclasses — não
implementa lógica de avaliação concreta. Define o que é uma capacidade
do sistema e os seus requisitos mínimos quantificados.

A *capacidade* é a entidade central do subsistema 3.4: representa algo
que o WorkStation AI 2 consegue disponibilizar (ex.: inferência local
de modelos, embeddings), definido de forma declarativa para que unidades
seguintes a possam avaliar contra o hardware e o runtime reais.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class CapabilityRequirements:
    """Requisitos mínimos para disponibilizar uma capacidade.

    Valores normalizados e comparáveis com o perfil de hardware
    (HardwareProfile) e o estado de runtime (RuntimeProfile). A
    avaliação concreta pertence a unidades futuras da Fase 4.
    """

    min_ram_gb: float = 1.0
    min_vram_gb: float | None = None
    min_cpu_cores: int = 1
    requires_gpu: bool = False
    min_available_disk_gb: float = 0.0

    @property
    def has_gpu_requirement(self) -> bool:
        """Indica se a capacidade exige GPU obrigatória."""
        return self.requires_gpu or self.min_vram_gb is not None


@dataclass(frozen=True)
class CapabilityDefinition:
    """Definição estrutural de uma capacidade do sistema.

    Representa o contrato declarativo de uma capacidade que o
    WorkStation AI 2 pode disponibilizar, incluindo os requisitos
    mínimos quantificados para a sua disponibilização.
    """

    id: str
    name: str
    description: str
    requirements: CapabilityRequirements = field(default_factory=CapabilityRequirements)

    @property
    def summary(self) -> str:
        """Resumo textual da capacidade para apresentação."""
        return f"{self.name} ({self.id})"


class CapabilityState(Enum):
    """Estados de avaliação de uma capacidade contra o sistema."""

    AVAILABLE = "available"      # Requisitos estruturais e runtime satisfeitos
    RESTRICTED = "restricted"    # Estruturalmente suportada, mas condicionada
    UNAVAILABLE = "unavailable"  # Requisitos mínimos não satisfeitos


@dataclass(frozen=True)
class RequirementCheck:
    """Resultado da verificação de um requisito individual.

    Regista o requisito (valor exigido), o que está disponível no
    sistema e se foi satisfeito, permitindo justificar o veredicto.
    """

    name: str  # "ram_total", "ram_available", "cpu_cores", "gpu", "disk"
    required: float | int | bool | None
    available: float | int | bool | None
    satisfied: bool


@dataclass(frozen=True)
class CapabilityVerdict:
    """Veredicto de avaliação de uma capacidade contra o sistema.

    Combina o estado final com as verificações por requisito que o
    justificam. Distingue implicitamente requisitos estruturais
    (Hardware Capability) dos requisitos de runtime (Runtime State).
    """

    capability_id: str
    state: CapabilityState
    checks: tuple[RequirementCheck, ...] = field(default_factory=tuple)

    @property
    def is_available(self) -> bool:
        """Indica se a capacidade está disponível (não condicionada)."""
        return self.state == CapabilityState.AVAILABLE

    @property
    def summary(self) -> str:
        """Resumo textual do veredicto para apresentação."""
        labels = {
            CapabilityState.AVAILABLE: "disponível",
            CapabilityState.RESTRICTED: "condicionada",
            CapabilityState.UNAVAILABLE: "indisponível",
        }
        return f"{self.capability_id}: {labels[self.state]}"