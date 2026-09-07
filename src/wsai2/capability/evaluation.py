"""Avaliação de capacidades contra hardware e runtime.

Determina se uma capacidade está disponível no sistema corrente,
distinguindo requisitos estruturais (*Hardware Capability*) dos
requisitos de runtime (*Runtime State*), conforme a separação
fundamental da arquitectura (Artigo 5 da Constituição).

Um requisito estrutural falhado torna a capacidade **indisponível**
(o sistema não tem capacidade de hardware suficiente). Um requisito
de runtime falhado (ex.: pouca memória livre no momento) torna-a
**condicionada** — estruturalmente suportada, mas não executável já.
"""

from __future__ import annotations

from .base import (
    CapabilityDefinition,
    CapabilityState,
    CapabilityVerdict,
    RequirementCheck,
)
from .registry import CapabilityRegistry
from wsai2.hardware import HardwareProfile
from wsai2.runtime import RuntimeProfile

# Requisitos considerados estruturais (Hardware Capability).
# Tudo o resto é tratado como requisito de runtime (Runtime State).
_STRUCTURAL_CHECK_NAMES = frozenset({"ram_total", "cpu_cores", "gpu"})


def _best_vram_gb(hardware: HardwareProfile) -> float:
    """Maior VRAM (GB) entre as GPUs do sistema (0.0 sem GPU)."""
    if not hardware.gpus:
        return 0.0
    return max((g.vram_bytes or 0) / (1024 ** 3) for g in hardware.gpus)


def _total_storage_gb(hardware: HardwareProfile) -> float:
    """Espaço de armazenamento total (GB) do sistema."""
    return sum(s.total_bytes for s in hardware.storage) / (1024 ** 3)


def _build_checks(
    definition: CapabilityDefinition,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> tuple[RequirementCheck, ...]:
    """Constrói as verificações por requisito da capacidade."""
    req = definition.requirements
    checks: list[RequirementCheck] = []

    # RAM total (estrutural)
    checks.append(RequirementCheck(
        name="ram_total",
        required=req.min_ram_gb,
        available=round(hardware.memory.total_gb, 2),
        satisfied=hardware.memory.total_gb >= req.min_ram_gb,
    ))

    # RAM disponível (runtime)
    checks.append(RequirementCheck(
        name="ram_available",
        required=req.min_ram_gb,
        available=round(runtime.memory.available_gb, 2),
        satisfied=runtime.memory.available_gb >= req.min_ram_gb,
    ))

    # Cores físicos (estrutural)
    checks.append(RequirementCheck(
        name="cpu_cores",
        required=req.min_cpu_cores,
        available=hardware.cpu.physical_cores,
        satisfied=hardware.cpu.physical_cores >= req.min_cpu_cores,
    ))

    # GPU (estrutural, apenas quando exigido)
    if req.has_gpu_requirement:
        required_vram = req.min_vram_gb or 0.0
        best_vram = round(_best_vram_gb(hardware), 2)
        checks.append(RequirementCheck(
            name="gpu",
            required=required_vram,
            available=best_vram,
            satisfied=bool(hardware.gpus) and best_vram >= required_vram,
        ))

    # Espaço em disco (estrutural)
    total_disk_gb = round(_total_storage_gb(hardware), 2)
    checks.append(RequirementCheck(
        name="disk",
        required=req.min_available_disk_gb,
        available=total_disk_gb,
        satisfied=total_disk_gb >= req.min_available_disk_gb,
    ))

    return tuple(checks)


def _state_from_checks(checks: tuple[RequirementCheck, ...]) -> CapabilityState:
    """Deriva o estado final do veredicto a partir das verificações."""
    structural_ok = all(
        check.satisfied
        for check in checks
        if check.name in _STRUCTURAL_CHECK_NAMES
    )
    if not structural_ok:
        return CapabilityState.UNAVAILABLE

    runtime_ok = all(
        check.satisfied
        for check in checks
        if check.name not in _STRUCTURAL_CHECK_NAMES
    )
    if not runtime_ok:
        return CapabilityState.RESTRICTED

    return CapabilityState.AVAILABLE


def evaluate_capability(
    definition: CapabilityDefinition,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> CapabilityVerdict:
    """Avalia uma capacidade contra o hardware e o runtime do sistema.

    Devolve um :class:`CapabilityVerdict` com o estado final e as
    verificações por requisito que o justificam.
    """
    checks = _build_checks(definition, hardware, runtime)
    return CapabilityVerdict(
        capability_id=definition.id,
        state=_state_from_checks(checks),
        checks=checks,
    )


def evaluate_capabilities(
    registry: CapabilityRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> tuple[CapabilityVerdict, ...]:
    """Avalia todas as capacidades registadas contra o sistema.

    Devolve uma tupla com um veredicto por definição registada.
    """
    return tuple(
        evaluate_capability(definition, hardware, runtime)
        for definition in registry.all()
    )


def available_capabilities(
    registry: CapabilityRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> tuple[CapabilityVerdict, ...]:
    """Devolve apenas os veredictos de capacidades disponíveis.

    Corresponde ao item "capacidades disponíveis" do roadmap da
    Fase 4.
    """
    return tuple(
        verdict
        for verdict in evaluate_capabilities(registry, hardware, runtime)
        if verdict.is_available
    )


__all__ = [
    "available_capabilities",
    "evaluate_capabilities",
    "evaluate_capability",
]