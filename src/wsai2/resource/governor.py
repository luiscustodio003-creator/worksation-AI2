"""Governação de recursos (hardening 05 do CORE_HARDENING_PLAN).

Evolui a gestão de memória existente para governação de recursos **sem
duplicar mecanismos**: a medição estrutural continua no subsistema
``wsai2.hardware`` (Hardware Capability) e a medição momentânea no
``wsai2.runtime`` (Runtime State). Este módulo apenas cruza os perfis
existentes com um orçamento declarativo de ``ResourceLimit``
(``wsai2.extension``) e mantém o livro de alocações/reservas.

Responsabilidades:
- normalizar limites declarativos por dimensão conhecida;
- validar folga efectiva (capacidade estrutural e disponibilidade
  momentânea, descontando o já comprometido);
- reservar recursos (``allocate``) e libertá-los (``release``).

Fora de âmbito desta unidade: enforce de timeout/cancelamento (8.4) e
scheduling/gestor de execução (8.5) — o governador não agenda nem lança
tarefas.

Dimensões sem leitura de runtime (VRAM em uso, espaço livre de disco)
são governadas pela capacidade estrutural; ``available_now`` fica
``None`` e a limitação é explicitada.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING

from wsai2.core.errors import ResourceError
from wsai2.hardware import HardwareProfile
from wsai2.runtime import RuntimeProfile

from .base import (
    AllocationState,
    ResourceAllocation,
    ResourceBudgetResult,
    ResourceCheck,
    ResourceDimension,
    ResourceVerdict,
)

if TYPE_CHECKING:
    from wsai2.extension import ResourceLimit

_BYTES_PER_GB = 1024 ** 3
_MB_TO_GB = 1.0 / 1024.0

# Mapa de nomes de limites conhecidos -> (dimensão, multiplicador para
# gigabytes). Em ``cpu`` a unidade natural é núcleos (multiplicador 1.0).
# Nomes fora deste mapa produzem veredicto UNRECOGNIZED — nunca silêncio.
_DIMENSION_MAP: dict[str, tuple[ResourceDimension, float]] = {
    "ram": (ResourceDimension.RAM, 1.0),
    "memory": (ResourceDimension.RAM, 1.0),
    "ram_gb": (ResourceDimension.RAM, 1.0),
    "memory_gb": (ResourceDimension.RAM, 1.0),
    "ram_mb": (ResourceDimension.RAM, _MB_TO_GB),
    "memory_mb": (ResourceDimension.RAM, _MB_TO_GB),
    "ram_total": (ResourceDimension.RAM, 1.0),
    "ram_available": (ResourceDimension.RAM, 1.0),
    "cpu": (ResourceDimension.CPU, 1.0),
    "cpu_cores": (ResourceDimension.CPU, 1.0),
    "vram": (ResourceDimension.VRAM, 1.0),
    "vram_gb": (ResourceDimension.VRAM, 1.0),
    "vram_mb": (ResourceDimension.VRAM, _MB_TO_GB),
    "disk": (ResourceDimension.DISK, 1.0),
    "storage": (ResourceDimension.DISK, 1.0),
    "disk_gb": (ResourceDimension.DISK, 1.0),
    "storage_gb": (ResourceDimension.DISK, 1.0),
    "disk_mb": (ResourceDimension.DISK, _MB_TO_GB),
    "storage_mb": (ResourceDimension.DISK, _MB_TO_GB),
}


class ResourceGovernor:
    """Governador de recursos sobre perfis estruturais e de runtime.

    Valida orçamentos declarativos contra ``HardwareProfile`` +
    ``RuntimeProfile`` e mantém, por instância, o livro de alocações.
    Cada instância é independente (sem estado global); o chamador pode
    criar um governador por ambiente/execução conforme a estratégia.
    """

    def __init__(self, hardware: HardwareProfile, runtime: RuntimeProfile) -> None:
        """Cria um governador ancorado a um estado estrutural e de runtime.

        Args:
            hardware: perfil estrutural (Hardware Capability).
            runtime: estado momentâneo (Runtime State).
        """
        self._hardware = hardware
        self._runtime = runtime
        self._allocations: dict[str, ResourceAllocation] = {}
        self._seq = 0

    def _capacity(self, dimension: ResourceDimension) -> float | None:
        """Capacidade estrutural total disponível na dimensão."""
        if dimension is ResourceDimension.RAM:
            return self._hardware.memory.total_gb
        if dimension is ResourceDimension.CPU:
            return float(self._hardware.cpu.physical_cores)
        if dimension is ResourceDimension.VRAM:
            if not self._hardware.gpus:
                return 0.0
            return max(
                (gpu.vram_bytes or 0) / _BYTES_PER_GB for gpu in self._hardware.gpus
            )
        if dimension is ResourceDimension.DISK:
            return sum(disk.total_bytes for disk in self._hardware.storage) / _BYTES_PER_GB
        return None

    def _available_now(self, dimension: ResourceDimension) -> float | None:
        """Disponibilidade momentânea efectiva na dimensão.

        Sem leitura de runtime para a dimensão (VRAM em uso, espaço livre
        em disco), devolve ``None`` — a governação usa a capacidade.
        """
        if dimension is ResourceDimension.RAM:
            return self._runtime.memory.available_gb
        if dimension is ResourceDimension.CPU:
            # Núcleos livres derivados da carga momentânea global.
            return self._runtime.cpu.count * (100.0 - self._runtime.cpu.percent) / 100.0
        return None

    def _committed(self, dimension: ResourceDimension) -> float:
        """Soma do valor já comprometido por alocações activas."""
        total = 0.0
        for allocation in self._allocations.values():
            if not allocation.is_active:
                continue
            for check in allocation.checks:
                if check.dimension is dimension:
                    total += check.required
        return total

    def committed_for(self, dimension: ResourceDimension) -> float:
        """Valor comprometido numa dimensão por alocações activas."""
        return self._committed(dimension)

    def _normalize(self, limit: ResourceLimit) -> ResourceCheck:
        """Normaliza um limite declarativo numa verificação de governação."""
        resolved = _DIMENSION_MAP.get(limit.name)
        if resolved is None:
            return ResourceCheck(
                name=limit.name,
                dimension=None,
                required=float(limit.value),
                capacity=None,
                available_now=None,
                committed=0.0,
                satisfied=False,
                verdict=ResourceVerdict.UNRECOGNIZED,
            )
        dimension, multiplier = resolved
        required = max(0.0, float(limit.value) * multiplier)
        capacity = self._capacity(dimension)
        available_now = self._available_now(dimension)
        committed = self._committed(dimension)

        folga = math.inf
        if capacity is not None:
            folga = min(folga, capacity - committed)
        if available_now is not None:
            folga = min(folga, available_now - committed)

        satisfied = required <= folga
        verdict = ResourceVerdict.AVAILABLE if satisfied else ResourceVerdict.UNAVAILABLE
        return ResourceCheck(
            name=limit.name,
            dimension=dimension,
            required=required,
            capacity=capacity,
            available_now=available_now,
            committed=committed,
            satisfied=satisfied,
            verdict=verdict,
        )

    def evaluate(self, budget: tuple[ResourceLimit, ...]) -> ResourceBudgetResult:
        """Avalia um orçamento de recursos contra o sistema actual.

        Não altera o livro de alocações — é uma consulta. Um orçamento
        vazio é satisfeito por vacuidade.

        Args:
            budget: limites declarativos (ex.: ``ExecutionContext.budget``).

        Returns:
            Resultado com verificações por dimensão.
        """
        checks = tuple(self._normalize(limit) for limit in budget)
        return ResourceBudgetResult(checks=checks)

    def _next_id(self, owner: str) -> str:
        """Gera um identificador de alocação único na instância."""
        self._seq += 1
        base = owner or "anonimo"
        return f"{base}:{self._seq}"

    def allocate(
        self,
        owner: str,
        budget: tuple[ResourceLimit, ...],
        *,
        allocation_id: str | None = None,
    ) -> ResourceAllocation:
        """Reserva recursos para um dono, se o orçamento estiver satisfeito.

        Avalia o orçamento contra o sistema (descontando o já
        comprometido) e, se satisfeito, regista uma alocação activa que
        passa a comprometer os valores pretendidos.

        Args:
            owner: dono da reserva (tipicamente um id de execução).
            budget: limites declarativos a reservar.
            allocation_id: identificador opcional; gerado se omisso.

        Returns:
            A alocação activa criada.

        Raises:
            ResourceError: se o orçamento não estiver satisfeito ou o
                identificador já estiver em uso.
        """
        result = self.evaluate(budget)
        if not result.is_available:
            details = {check.name: check.summary for check in result.unavailable_checks}
            raise ResourceError(
                f"orçamento de recursos insatisfeito para {owner}",
                code="wsai.resource.insufficient",
                details=details,
            )
        alloc_id = allocation_id or self._next_id(owner)
        if alloc_id in self._allocations:
            raise ResourceError(
                f"alocação já registada: {alloc_id}",
                code="wsai.resource.duplicate",
            )
        allocation = ResourceAllocation(
            allocation_id=alloc_id,
            owner=owner,
            checks=result.checks,
            state=AllocationState.ACTIVE,
        )
        self._allocations[alloc_id] = allocation
        return allocation

    def release(self, allocation_id: str) -> ResourceAllocation:
        """Liberta uma alocação, devolvendo os recursos comprometidos.

        A libertação é idempotente: uma alocação já libertada devolve-se
        tal como está, sem erro.

        Args:
            allocation_id: identificador da alocação a libertar.

        Returns:
            A alocação no estado libertado.

        Raises:
            ResourceError: se a alocação for desconhecida.
        """
        allocation = self._allocations.get(allocation_id)
        if allocation is None:
            raise ResourceError(
                f"alocação desconhecida: {allocation_id}",
                code="wsai.resource.unknown",
            )
        if not allocation.is_active:
            return allocation
        released = replace(allocation, state=AllocationState.RELEASED)
        self._allocations[allocation_id] = released
        return released

    @property
    def outstanding(self) -> tuple[ResourceAllocation, ...]:
        """Alocações activas (reservas em vigor)."""
        return tuple(a for a in self._allocations.values() if a.is_active)


__all__ = ["ResourceGovernor"]