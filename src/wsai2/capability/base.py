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

from wsai2.hardware import CapabilityDomain


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
    mínimos quantificados para a sua disponibilização e o domínio de
    capacidade a que pertence (COMPUTE, MEMORY, GRAPHICS, STORAGE).
    """

    id: str
    name: str
    description: str
    requirements: CapabilityRequirements = field(default_factory=CapabilityRequirements)
    domain: CapabilityDomain = CapabilityDomain.COMPUTE

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


# Rótulos em português por requisito, para apresentação em linguagem natural.
_REQUIREMENT_LABELS = {
    "ram_total": "RAM total",
    "ram_available": "RAM disponível",
    "cpu_cores": "processadores (cores)",
    "gpu": "GPU/VRAM",
    "disk": "espaço em disco",
}


def _format_valor(valor: float | int | bool | None) -> str:
    """Formata um valor de requisito ou recurso para justificação textual."""
    if isinstance(valor, bool):
        return "sim" if valor else "não"
    if valor is None:
        return "sem informação"
    return str(valor)


@dataclass(frozen=True)
class CapabilityCompatibility:
    """Compatibilidade de uma capacidade com o sistema actual.

    Associa a definição estrutural da capacidade ao veredicto da sua
    avaliação contra o hardware e o runtime, e apresenta uma
    justificação textual que explica o estado em linguagem natural.
    """

    definition: CapabilityDefinition
    verdict: CapabilityVerdict

    @property
    def state(self) -> CapabilityState:
        """Estado de compatibilidade da capacidade."""
        return self.verdict.state

    @property
    def is_available(self) -> bool:
        """Indica se a capacidade está disponível no momento."""
        return self.verdict.is_available

    @property
    def justification(self) -> str:
        """Justificação textual do estado de compatibilidade.

        Explica porque a capacidade está disponível, condicionada ou
        indisponível, enumerando os requisitos não satisfeitos com os
        valores exigidos e os valores disponíveis no sistema.
        """
        if self.verdict.state == CapabilityState.AVAILABLE:
            return "Capacidade disponível: todos os requisitos estão satisfeitos."

        falhados = [check for check in self.verdict.checks if not check.satisfied]
        detalhes = [
            f"{_REQUIREMENT_LABELS.get(check.name, check.name)} — "
            f"exigido {_format_valor(check.required)}, "
            f"disponível {_format_valor(check.available)}"
            for check in falhados
        ]
        if self.verdict.state == CapabilityState.RESTRICTED:
            prefixo = "Capacidade estruturalmente suportada, mas condicionada no momento"
        else:
            prefixo = "Requisitos estruturais não satisfeitos"
        return f"{prefixo}: {'; '.join(detalhes)}."


@dataclass(frozen=True)
class CompatibilityReport:
    """Relatório consolidado de compatibilidade do sistema.

    Reúne, para cada capacidade conhecida do registo, a sua
    compatibilidade com o hardware e o runtime actuais. Disponibiliza
    agrupamentos por estado e o catálogo final de capacidades
    disponíveis — correspondente ao item "capacidades disponíveis" do
    roadmap da Fase 4.
    """

    hardware: "HardwareProfile"
    runtime: "RuntimeProfile"
    entries: tuple[CapabilityCompatibility, ...] = field(default_factory=tuple)

    def _by_state(self, state: CapabilityState) -> tuple[CapabilityCompatibility, ...]:
        """Entradas do relatório num determinado estado."""
        return tuple(entry for entry in self.entries if entry.state is state)

    def by_domain(
        self, domain: CapabilityDomain
    ) -> tuple[CapabilityCompatibility, ...]:
        """Entradas do relatório num determinado domínio de capacidade."""
        return tuple(entry for entry in self.entries if entry.definition.domain is domain)

    @property
    def available(self) -> tuple[CapabilityCompatibility, ...]:
        """Capacidades disponíveis (catálogo final)."""
        return self._by_state(CapabilityState.AVAILABLE)

    @property
    def restricted(self) -> tuple[CapabilityCompatibility, ...]:
        """Capacidades estruturalmente suportadas mas condicionadas."""
        return self._by_state(CapabilityState.RESTRICTED)

    @property
    def unavailable(self) -> tuple[CapabilityCompatibility, ...]:
        """Capacidades indisponíveis por requisitos estruturais."""
        return self._by_state(CapabilityState.UNAVAILABLE)

    @property
    def summary(self) -> str:
        """Resumo textual do relatório para apresentação."""
        return (
            f"{len(self.available)} capacidades disponíveis, "
            f"{len(self.restricted)} condicionadas, "
            f"{len(self.unavailable)} indisponíveis"
        )