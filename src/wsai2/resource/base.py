"""Contratos e tipos fundamentais da Governação de Recursos.

Este módulo contém apenas definições de tipos e dataclasses — não
implementa lógica de validação nem accounting. Garante que a governação
depende de contratos estáveis (hardening 05 do CORE_HARDENING_PLAN),
sem duplicar a medição de hardware (subsistema ``wsai2.hardware``) nem a
medição de runtime (subsistema ``wsai2.runtime``).

Os contratos aqui definidos representam *decisões* de governação:
veredictos por dimensão, resultados de avaliação de um orçamento e
alocações/reservas efectuadas pelo governador. A capacidade estrutural e
a disponibilidade momentânea são referidas por valor (``capacity`` e
``available_now``) já resolvidas contra os perfis existentes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResourceDimension(Enum):
    """Dimensões de recursos governáveis no WorkStation AI 2.

    A lista cobre os recursos previstos no hardening 05, segundo os
    dados já expostos pelos subsistemas Hardware e Runtime Intelligence.
    Dimensões sem leitura de runtime (ex.: VRAM em uso) são governadas
    apenas pela capacidade estrutural — limitação documentada.
    """

    RAM = "ram"        # Memória RAM
    CPU = "cpu"        # Núcleos de processamento
    VRAM = "vram"      # Memória gráfica (GPU)
    DISK = "disk"      # Armazenamento


class ResourceVerdict(Enum):
    """Veredictos de governação para uma dimensão de recurso."""

    AVAILABLE = "available"        # Limite satisfeito pelo sistema
    UNAVAILABLE = "unavailable"    # Limite não satisfeito pelo sistema
    UNRECOGNIZED = "unrecognized"  # Nome de limite não reconhecido


class AllocationState(Enum):
    """Estados de uma alocação/reserva de recursos."""

    ACTIVE = "active"      # Reserva em vigor (recursos comprometidos)
    RELEASED = "released"  # Reserva libertada (recursos retornados)


@dataclass(frozen=True)
class ResourceCheck:
    """Avaliação de um limite de recurso contra o sistema.

    Cruza o valor exigido (``required``) com a capacidade estrutural
    (``capacity``), a disponibilidade momentânea (``available_now``) e o
    valor já comprometido por alocações activas (``committed``). Quando
    uma dimensão não tem leitura de runtime, ``available_now`` é ``None``
    e a governação usa apenas a capacidade estrutural.

    Attributes:
        name: nome original do limite declarado (ex.: ``memory_mb``).
        dimension: dimensão reconhecida, ou ``None`` se não reconhecida.
        required: valor exigido normalizado (GB, ou núcleos em ``cpu``).
        capacity: capacidade estrutural total disponível, se conhecida.
        available_now: disponibilidade momentânea, se conhecida.
        committed: valor já comprometido por alocações activas.
        satisfied: indica se o limite está satisfeito.
        verdict: veredicto de governação desta dimensão.
    """

    name: str
    dimension: ResourceDimension | None
    required: float
    capacity: float | None
    available_now: float | None
    committed: float
    satisfied: bool
    verdict: ResourceVerdict

    @property
    def is_recognized(self) -> bool:
        """Indica se a dimensão do limite foi reconhecida."""
        return self.dimension is not None

    @property
    def summary(self) -> str:
        """Resumo textual da verificação para apresentação."""
        dimensao = self.dimension.value if self.dimension else "desconhecido"
        estado = "satisfeito" if self.satisfied else "insatisfeito"
        return f"{self.name} ({dimensao}) requer {self.required:.3g} -> {estado}"


@dataclass(frozen=True)
class ResourceBudgetResult:
    """Resultado de avaliar um orçamento de recursos.

    Reúne as verificações por dimensão de um orçamento declarativo.
    Um orçamento vazio é satisfeito por vacuidade (sem limites, não há
    pretensão que falhe).
    """

    checks: tuple[ResourceCheck, ...]

    @property
    def is_available(self) -> bool:
        """Indica se todos os limites do orçamento estão satisfeitos."""
        return all(check.satisfied for check in self.checks)

    @property
    def available_checks(self) -> tuple[ResourceCheck, ...]:
        """Verificações satisfeitas."""
        return tuple(check for check in self.checks if check.satisfied)

    @property
    def unavailable_checks(self) -> tuple[ResourceCheck, ...]:
        """Verificações insatisfeitas (incluindo não reconhecidas)."""
        return tuple(check for check in self.checks if not check.satisfied)

    @property
    def unrecognized_checks(self) -> tuple[ResourceCheck, ...]:
        """Verificações com dimensão não reconhecida."""
        return tuple(
            check for check in self.checks if check.verdict is ResourceVerdict.UNRECOGNIZED
        )

    @property
    def summary(self) -> str:
        """Resumo textual do resultado para apresentação."""
        if not self.checks:
            return "orçamento vazio (sem limites)"
        if self.is_available:
            return f"orçamento satisfeito ({len(self.checks)} limites)"
        return (
            f"orçamento insatisfeito: "
            f"{len(self.unavailable_checks)}/{len(self.checks)} limites em falha"
        )


@dataclass(frozen=True)
class ResourceAllocation:
    """Reserva de recursos efectuada pelo governador.

    Regista a pretensão aprovada (as verificações satisfeitas) para um
    dono (``owner``, tipicamente um id de execução/contexto) sobre um
    conjunto de limites. Uma alocação activa compromete recursos até ser
    libertada.
    """

    allocation_id: str
    owner: str
    checks: tuple[ResourceCheck, ...]
    state: AllocationState = AllocationState.ACTIVE

    @property
    def is_active(self) -> bool:
        """Indica se a alocação ainda está em vigor."""
        return self.state is AllocationState.ACTIVE

    @property
    def summary(self) -> str:
        """Resumo textual da alocação para apresentação."""
        estado = "activa" if self.is_active else "libertada"
        return f"alocação {self.allocation_id} ({self.owner}) {estado}"


__all__ = [
    "AllocationState",
    "ResourceAllocation",
    "ResourceBudgetResult",
    "ResourceCheck",
    "ResourceDimension",
    "ResourceVerdict",
]