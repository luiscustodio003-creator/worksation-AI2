"""Análise de disponibilidade efectiva do runtime.

Este módulo implementa a lógica para transformar o estado de runtime
bruto (CpuLoad, MemoryRuntime) em disponibilidade derivada por domínio
(RuntimeAvailability) e um estado global (AvailabilityStatus).

A disponibilidade representa até que ponto os recursos estão de facto
livres para trabalho no momento da amostragem — distinta da capacidade
estrutural avaliada pelo Hardware Intelligence.
"""

from __future__ import annotations

from .base import (
    AvailabilityDomain,
    AvailabilityStatus,
    CpuLoad,
    MemoryRuntime,
    RuntimeAvailability,
)


def _status_from_score(score: float) -> AvailabilityStatus:
    """Converte score de disponibilidade (0.0 a 1.0) em estado."""
    if score >= 0.8:
        return AvailabilityStatus.HEALTHY
    if score >= 0.5:
        return AvailabilityStatus.DEGRADED
    return AvailabilityStatus.CRITICAL


def analyze_cpu_availability(cpu: CpuLoad) -> RuntimeAvailability:
    """Calcula a disponibilidade de processamento a partir da carga."""
    # Disponibilidade = capacidade livre (1 - carga normalizada)
    # Carga de 0% → disponibilidade 1.0; 100% → 0.0
    available_fraction = max(0.0, min(1.0, (100.0 - cpu.percent) / 100.0))

    # Penalizar saturação: mesmo com picos recentes, sinal clara de pressão
    score = available_fraction
    if cpu.is_saturated:
        score *= 0.5

    return RuntimeAvailability(
        domain=AvailabilityDomain.CPU,
        score=round(score, 3),
        status=_status_from_score(score),
        details={
            "load_percent": round(cpu.percent, 1),
            "saturated": cpu.is_saturated,
            "idle": cpu.is_idle,
            "cores": cpu.count,
        },
    )


def analyze_memory_availability(memory: MemoryRuntime) -> RuntimeAvailability:
    """Calcula a disponibilidade de memória a partir do uso efectivo."""
    # Disponibilidade = percentagem livre
    score = max(0.0, min(1.0, memory.free_percent / 100.0))

    # Pressão de swap reduz a disponibilidade efectiva
    swap_pressure = 0.0
    if memory.swap_total_bytes > 0:
        swap_pressure = memory.swap_percent / 100.0
        # Aplicar penalização moderada até 30%
        score *= 1.0 - (swap_pressure * 0.3)

    return RuntimeAvailability(
        domain=AvailabilityDomain.MEMORY,
        score=round(max(0.0, score), 3),
        status=_status_from_score(score),
        details={
            "used_percent": round(memory.percent, 1),
            "free_percent": round(memory.free_percent, 1),
            "available_gb": round(memory.available_gb, 2),
            "swap_pressure": round(swap_pressure, 3),
        },
    )


def analyze_runtime_availability(
    cpu: CpuLoad,
    memory: MemoryRuntime,
) -> tuple[RuntimeAvailability, ...]:
    """Analisa o estado de runtime e devolve disponibilidades por domínio."""
    return (
        analyze_cpu_availability(cpu),
        analyze_memory_availability(memory),
    )


def _overall_status(availability: tuple[RuntimeAvailability, ...]) -> AvailabilityStatus:
    """Calcula o estado global de disponibilidade ponderado.

    A memória tem peso ligeiramente superior por ser o recurso que
    limita a execução de modelos de IA no sistema.
    """
    if not availability:
        return AvailabilityStatus.HEALTHY

    weights = {
        AvailabilityDomain.CPU: 0.45,
        AvailabilityDomain.MEMORY: 0.55,
    }

    weighted_sum = 0.0
    total_weight = 0.0
    for avail in availability:
        weight = weights.get(avail.domain, 0.0)
        if weight > 0:
            weighted_sum += avail.score * weight
            total_weight += weight

    if total_weight == 0:
        return AvailabilityStatus.HEALTHY

    return _status_from_score(weighted_sum / total_weight)


__all__ = [
    "analyze_cpu_availability",
    "analyze_memory_availability",
    "analyze_runtime_availability",
    "_overall_status",
]