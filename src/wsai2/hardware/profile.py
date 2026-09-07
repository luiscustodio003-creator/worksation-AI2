"""Análise e agregação de perfil de hardware com capacidades derivadas.

Este módulo implementa a lógica para transformar dados brutos de hardware
(CpuInfo, MemoryInfo, GpuInfo, StorageInfo) em capacidades estruturais
quantificadas (HardwareCapability) e um perfil agregado com nível global.
"""

from __future__ import annotations

from .base import (
    Architecture,
    CapabilityDomain,
    CapabilityLevel,
    CpuInfo,
    GpuInfo,
    HardwareCapability,
    HardwareProfile,
    MemoryInfo,
    StorageInfo,
)


def _score_cpu(cpu: CpuInfo) -> float:
    """Calcula score de capacidade de computação (0.0 a 1.0)."""
    # Base: cores físicos (normalizado para 16 cores = 1.0)
    core_score = min(cpu.physical_cores / 16.0, 1.0) * 0.4

    # Frequência (normalizado para 5 GHz = 1.0)
    freq_score = 0.0
    if cpu.max_frequency_mhz:
        freq_score = min(cpu.max_frequency_mhz / 5000.0, 1.0) * 0.2

    # Arquitectura (bonificação para arquitecturas modernas)
    arch_score = 0.1
    if cpu.architecture in (Architecture.X86_64, Architecture.ARM64):
        arch_score = 0.15

    # Hyperthreading/SMT
    ht_score = 0.1 if cpu.has_hyperthreading else 0.0

    # Cache L3 (se disponível)
    cache_score = 0.0
    if cpu.cache_l3_kb:
        cache_score = min(cpu.cache_l3_kb / 32768.0, 1.0) * 0.15  # 32MB = 1.0

    # Features especiais (AVX, AVX2, AVX-512, NEON, etc.)
    feature_score = 0.0
    feature_flags = set(cpu.features)
    if any(f in feature_flags for f in ("avx512f", "avx512")):
        feature_score = 0.1
    elif any(f in feature_flags for f in ("avx2", "avx")):
        feature_score = 0.05
    elif "neon" in feature_flags:
        feature_score = 0.05

    return min(core_score + freq_score + arch_score + ht_score + cache_score + feature_score, 1.0)


def _score_memory(memory: MemoryInfo) -> float:
    """Calcula score de capacidade de memória (0.0 a 1.0)."""
    # Normalizado para 64GB = 1.0
    gb = memory.total_gb
    return min(gb / 64.0, 1.0)


def _score_graphics(gpus: tuple[GpuInfo, ...]) -> float:
    """Calcula score de capacidade gráfica (0.0 a 1.0)."""
    if not gpus:
        return 0.0

    best_score = 0.0
    for gpu in gpus:
        score = 0.0
        # VRAM (normalizado para 24GB = 1.0)
        if gpu.vram_bytes:
            vram_gb = gpu.vram_bytes / (1024 ** 3)
            score += min(vram_gb / 24.0, 1.0) * 0.6

        # Vendor bonus (NVIDIA/AMD modernos)
        vendor_lower = gpu.vendor.lower()
        if vendor_lower in ("nvidia", "amd"):
            score += 0.2
        elif vendor_lower == "intel":
            score += 0.1

        # Nome sugere geração moderna
        name_lower = gpu.name.lower()
        if any(kw in name_lower for kw in ("rtx", "rx 6", "rx 7", "arc")):
            score += 0.2

        best_score = max(best_score, min(score, 1.0))

    return best_score


def _score_storage(storage: tuple[StorageInfo, ...]) -> float:
    """Calcula score de capacidade de armazenamento (0.0 a 1.0)."""
    if not storage:
        return 0.0

    # Total space (normalizado para 2TB = 1.0)
    total_gb = sum(s.total_bytes for s in storage) / (1024 ** 3)
    space_score = min(total_gb / 2048.0, 1.0) * 0.5

    # Tipo de disco (NVMe > SSD > HDD)
    type_score = 0.0
    types = {s.type for s in storage}
    if "nvme" in types:
        type_score = 0.5
    elif "ssd" in types:
        type_score = 0.35
    elif "hdd" in types:
        type_score = 0.15

    return min(space_score + type_score, 1.0)


def _level_from_score(score: float) -> CapabilityLevel:
    """Converte score numérico em nível de capacidade."""
    if score >= 0.8:
        return CapabilityLevel.HIGH_END
    if score >= 0.6:
        return CapabilityLevel.ADVANCED
    if score >= 0.4:
        return CapabilityLevel.INTERMEDIATE
    if score >= 0.2:
        return CapabilityLevel.BASIC
    return CapabilityLevel.MINIMAL


def _overall_level(capabilities: tuple[HardwareCapability, ...]) -> CapabilityLevel:
    """Calcula nível global baseado nas capacidades individuais."""
    if not capabilities:
        return CapabilityLevel.MINIMAL

    # Média ponderada: compute e memory têm peso maior
    weights = {
        CapabilityDomain.COMPUTE: 0.35,
        CapabilityDomain.MEMORY: 0.25,
        CapabilityDomain.GRAPHICS: 0.20,
        CapabilityDomain.STORAGE: 0.20,
    }

    weighted_sum = 0.0
    total_weight = 0.0
    for cap in capabilities:
        weight = weights.get(cap.domain, 0.0)
        if weight > 0:
            # Converter nível para score numérico
            level_scores = {
                CapabilityLevel.MINIMAL: 0.1,
                CapabilityLevel.BASIC: 0.3,
                CapabilityLevel.INTERMEDIATE: 0.5,
                CapabilityLevel.ADVANCED: 0.75,
                CapabilityLevel.HIGH_END: 1.0,
            }
            weighted_sum += level_scores[cap.level] * weight
            total_weight += weight

    if total_weight == 0:
        return CapabilityLevel.MINIMAL

    avg_score = weighted_sum / total_weight
    return _level_from_score(avg_score)


def analyze_hardware_profile(
    cpu: CpuInfo,
    memory: MemoryInfo,
    gpus: tuple[GpuInfo, ...],
    storage: tuple[StorageInfo, ...],
) -> HardwareProfile:
    """Analisa hardware bruto e produz perfil com capacidades derivadas."""

    # Calcular scores por domínio
    compute_score = _score_cpu(cpu)
    memory_score = _score_memory(memory)
    graphics_score = _score_graphics(gpus)
    storage_score = _score_storage(storage)

    # Criar capacidades estruturais
    capabilities = (
        HardwareCapability(
            domain=CapabilityDomain.COMPUTE,
            score=compute_score,
            level=_level_from_score(compute_score),
            details={
                "physical_cores": cpu.physical_cores,
                "logical_cores": cpu.logical_cores,
                "max_frequency_mhz": cpu.max_frequency_mhz or 0,
                "architecture": cpu.architecture.value,
                "has_hyperthreading": cpu.has_hyperthreading,
            },
        ),
        HardwareCapability(
            domain=CapabilityDomain.MEMORY,
            score=memory_score,
            level=_level_from_score(memory_score),
            details={
                "total_gb": round(memory.total_gb, 1),
                "has_swap": memory.has_swap,
                "swap_gb": round(memory.swap_total_gb, 1),
            },
        ),
        HardwareCapability(
            domain=CapabilityDomain.GRAPHICS,
            score=graphics_score,
            level=_level_from_score(graphics_score),
            details={
                "gpu_count": len(gpus),
                "best_vram_gb": round(max((g.vram_bytes or 0) / (1024**3) for g in gpus), 1) if gpus else 0,
                "vendors": list({g.vendor for g in gpus}),
            },
        ),
        HardwareCapability(
            domain=CapabilityDomain.STORAGE,
            score=storage_score,
            level=_level_from_score(storage_score),
            details={
                "device_count": len(storage),
                "total_gb": round(sum(s.total_bytes for s in storage) / (1024**3), 1),
                "types": list({s.type for s in storage}),
            },
        ),
    )

    overall = _overall_level(capabilities)

    return HardwareProfile(
        cpu=cpu,
        memory=memory,
        gpus=gpus,
        storage=storage,
        capabilities=capabilities,
        overall_level=overall,
    )


__all__ = ["analyze_hardware_profile"]