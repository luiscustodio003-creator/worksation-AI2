"""Compatibilidade de modelos contra hardware, runtime e capacidades.

Determina se um modelo conhecido está disponível neste sistema,
combinando três dimensões:

1. **Capacidades do sistema** — as capacidades requeridas pelo modelo
   (via ``ModelRequirements.required_capabilities``) devem existir e
   estar estruturalmente suportadas no Capability Engine;
2. **Requisitos estruturais** do modelo (RAM total, cores, GPU) —
   *Hardware Capability*;
3. **Requisitos de runtime** do modelo (RAM disponível, disco) —
   *Runtime State*.

A separação entre capacidade estrutural e estado momentâneo respeita o
Artigo 5 da Constituição. Uma capacidade ausente ou requisito
estrutural falhado torna o modelo **indisponível**; uma capacidade
apenas condicionada ou falta de recursos momentâneos torna-o
**condicionado**. Este módulo apenas avalia — não recomenda nem
classifica modelos (responsabilidades de unidades seguintes).
"""

from __future__ import annotations

from .base import (
    ModelCheck,
    ModelDefinition,
    ModelState,
    ModelVerdict,
)
from .registry import ModelRegistry
from wsai2.capability import CapabilityRegistry, CapabilityState, evaluate_capability
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


def _capability_availability(
    definition: ModelDefinition,
    capability_registry: CapabilityRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
) -> tuple[list[str], list[str]]:
    """Devolve (faltantes, condicionadas) entre as capacidades requeridas.

    Uma capacidade é *faltante* quando não está registada ou está
    estruturalmente indisponível (UNAVAILABLE). É *condicionada* quando
    está estruturalmente suportada mas não disponível já (RESTRICTED).
    """
    faltantes: list[str] = []
    condicionadas: list[str] = []
    for capability_id in definition.requirements.required_capabilities:
        capability = capability_registry.get(capability_id)
        if capability is None:
            faltantes.append(capability_id)
            continue
        verdict = evaluate_capability(capability, hardware, runtime)
        if verdict.state is CapabilityState.UNAVAILABLE:
            faltantes.append(capability_id)
        elif verdict.state is CapabilityState.RESTRICTED:
            condicionadas.append(capability_id)
    return faltantes, condicionadas


def _build_checks(
    definition: ModelDefinition,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
) -> tuple[ModelCheck, ...]:
    """Constrói as verificações por requisito do modelo."""
    req = definition.requirements
    checks: list[ModelCheck] = []
    faltantes, _ = _capability_availability(definition, capability_registry, hardware, runtime)

    requeridas = req.required_capabilities
    satisfeitas = tuple(cid for cid in requeridas if cid not in faltantes)
    checks.append(ModelCheck(
        name="capabilities",
        required=requeridas,
        available=satisfeitas,
        satisfied=not faltantes,
    ))

    # RAM total (estrutural)
    checks.append(ModelCheck(
        name="ram_total",
        required=req.min_ram_gb,
        available=round(hardware.memory.total_gb, 2),
        satisfied=hardware.memory.total_gb >= req.min_ram_gb,
    ))

    # RAM disponível (runtime)
    checks.append(ModelCheck(
        name="ram_available",
        required=req.min_ram_gb,
        available=round(runtime.memory.available_gb, 2),
        satisfied=runtime.memory.available_gb >= req.min_ram_gb,
    ))

    # Cores físicos (estrutural)
    checks.append(ModelCheck(
        name="cpu_cores",
        required=req.min_cpu_cores,
        available=hardware.cpu.physical_cores,
        satisfied=hardware.cpu.physical_cores >= req.min_cpu_cores,
    ))

    # GPU (estrutural, apenas quando exigido)
    if req.has_gpu_requirement:
        required_vram = req.min_vram_gb or 0.0
        best_vram = round(_best_vram_gb(hardware), 2)
        checks.append(ModelCheck(
            name="gpu",
            required=required_vram,
            available=best_vram,
            satisfied=bool(hardware.gpus) and best_vram >= required_vram,
        ))

    # Espaço em disco (estrutural)
    total_disk_gb = round(_total_storage_gb(hardware), 2)
    checks.append(ModelCheck(
        name="disk",
        required=req.min_available_disk_gb,
        available=total_disk_gb,
        satisfied=total_disk_gb >= req.min_available_disk_gb,
    ))

    return tuple(checks)


def _state_from_checks(
    checks: tuple[ModelCheck, ...],
    faltantes: tuple[str, ...],
    condicionadas: tuple[str, ...],
) -> ModelState:
    """Deriva o estado final do veredicto a partir das verificações."""
    structural_ok = all(
        check.satisfied
        for check in checks
        if check.name in _STRUCTURAL_CHECK_NAMES
    )
    if faltantes or not structural_ok:
        return ModelState.UNAVAILABLE

    runtime_ok = all(
        check.satisfied
        for check in checks
        if check.name not in _STRUCTURAL_CHECK_NAMES and check.name != "capabilities"
    )
    if condicionadas or not runtime_ok:
        return ModelState.RESTRICTED

    return ModelState.AVAILABLE


def evaluate_model(
    definition: ModelDefinition,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
) -> ModelVerdict:
    """Avalia a compatibilidade de um modelo contra o sistema.

    Verifica as capacidades requeridas através do Capability Engine e
    os requisitos estruturais e de runtime do modelo. Devolve um
    :class:`ModelVerdict` com o estado final e as verificações por
    requisito que o justificam.
    """
    faltantes, condicionadas = _capability_availability(
        definition, capability_registry, hardware, runtime
    )
    checks = _build_checks(definition, hardware, runtime, capability_registry)
    return ModelVerdict(
        model_id=definition.id,
        state=_state_from_checks(checks, tuple(faltantes), tuple(condicionadas)),
        checks=checks,
        missing_capabilities=tuple(faltantes),
    )


def evaluate_models(
    model_registry: ModelRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
) -> tuple[ModelVerdict, ...]:
    """Avalia todos os modelos registados contra o sistema.

    Devolve uma tupla com um veredicto por definição registada.
    """
    return tuple(
        evaluate_model(definition, hardware, runtime, capability_registry)
        for definition in model_registry.all()
    )


def compatible_models(
    model_registry: ModelRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
) -> tuple[ModelVerdict, ...]:
    """Devolve apenas os veredictos de modelos de facto compatíveis.

    Corresponde ao item "compatibilidade" do roadmap da Fase 5.
    """
    return tuple(
        verdict
        for verdict in evaluate_models(model_registry, hardware, runtime, capability_registry)
        if verdict.is_available
    )


__all__ = [
    "compatible_models",
    "evaluate_model",
    "evaluate_models",
]