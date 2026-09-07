"""Contratos e tipos fundamentais do Runtime Intelligence.

Este módulo contém apenas definições de tipos e dataclasses —
não implementa nenhuma lógica de descoberta concreta. Garante que o
domínio depende de contratos estáveis e não de detalhes de implementação.

O Runtime Intelligence representa o *Runtime State* (estado momentâneo
de execução), distinto de *Hardware Capability* (capacidade estrutural
descoberta pelo subsistema Hardware Intelligence).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


@dataclass(frozen=True)
class CpuLoad:
    """Estado de carga do processador num instante dado.

    Representa a utilização real do CPU no momento da amostragem.
    """

    percent: float          # Média global (0.0 a 100.0)
    per_core: tuple[float, ...] = field(default_factory=tuple)  # Por core
    count: int = 0          # Número de cores para os quais se obteve leitura
    frequency_current_mhz: float | None = None  # Frequência actual

    @property
    def is_idle(self) -> bool:
        """Indica se o CPU está ocioso (carga inferior a 10%)."""
        return self.percent < 10.0

    @property
    def is_saturated(self) -> bool:
        """Indica se o CPU está saturado (carga igual ou superior a 90%)."""
        return self.percent >= 90.0


@dataclass(frozen=True)
class MemoryRuntime:
    """Estado de utilização de memória no instante dado.

    Representa a utilização real de memória, distinta da capacidade
    estrutural (MemoryInfo) descoberta pelo Hardware Intelligence.
    """

    total_bytes: int
    available_bytes: int
    used_bytes: int
    percent: float              # 0.0 a 100.0
    swap_total_bytes: int = 0
    swap_used_bytes: int = 0
    swap_percent: float = 0.0

    @property
    def available_gb(self) -> float:
        """Memória disponível em gigabytes."""
        return self.available_bytes / (1024 ** 3)

    @property
    def used_gb(self) -> float:
        """Memória utilizada em gigabytes."""
        return self.used_bytes / (1024 ** 3)

    @property
    def total_gb(self) -> float:
        """Memória total em gigabytes."""
        return self.total_bytes / (1024 ** 3)

    @property
    def free_percent(self) -> float:
        """Percentagem de memória livre."""
        return 100.0 - self.percent

    @property
    def has_swap_active(self) -> bool:
        """Indica se há swap em utilização efectiva."""
        return self.swap_used_bytes > 0


@dataclass(frozen=True)
class ProcessInfo:
    """Informação resumida de um processo activo.

    Representa os processos mais relevantes no momento da amostragem,
    úteis para compreender a utilização de recursos do sistema.
    """

    pid: int
    name: str
    status: str  # "running", "sleeping", "stopped", etc.
    cpu_percent: float
    memory_rss_bytes: int
    memory_percent: float

    @property
    def memory_rss_mb(self) -> float:
        """Memória RSS do processo em megabytes."""
        return self.memory_rss_bytes / (1024 ** 2)


@dataclass(frozen=True)
class SystemUptime:
    """Tempo de actividade do sistema."""

    boot_timestamp: float    # time.time() do boot
    uptime_seconds: float

    @property
    def uptime_hours(self) -> float:
        """Uptime em horas."""
        return self.uptime_seconds / 3600.0

    @property
    def uptime_days(self) -> float:
        """Uptime em dias."""
        return self.uptime_seconds / 86400.0


class AvailabilityDomain(Enum):
    """Domínios de disponibilidade de runtime."""

    CPU = "cpu"          # Disponibilidade de processamento
    MEMORY = "memory"    # Disponibilidade de memória


class AvailabilityStatus(Enum):
    """Estados de disponibilidade efectiva dos recursos."""

    HEALTHY = "healthy"      # Recursos amplamente disponíveis
    DEGRADED = "degraded"    # Recursos disponíveis com restrições
    CRITICAL = "critical"    # Recursos escassos / sob pressão


@dataclass(frozen=True)
class RuntimeAvailability:
    """Disponibilidade efectiva derivada num domínio de runtime.

    Representa a avaliação derivada do estado de execução actual:
    até que ponto os recursos estão de facto disponíveis para trabalho.
    """

    domain: AvailabilityDomain
    score: float  # 0.0 a 1.0 (1.0 = totalmente disponível)
    status: AvailabilityStatus
    details: dict[str, str | int | float] = field(default_factory=dict)

    @property
    def is_available(self) -> bool:
        """Indica se o recurso está suficientemente disponível."""
        return self.status != AvailabilityStatus.CRITICAL


@dataclass(frozen=True)
class RuntimeProfile:
    """Perfil completo do estado de runtime do sistema.

    Agrega toda a informação de runtime descoberta num instante.
    Representa *Runtime State* (estado momentâneo de execução) —
    distinto de *Hardware Capability* (capacidade estrutural).
    """

    cpu: CpuLoad
    memory: MemoryRuntime
    processes: tuple[ProcessInfo, ...] = field(default_factory=tuple)
    uptime: SystemUptime | None = None
    availability: tuple[RuntimeAvailability, ...] = field(default_factory=tuple)
    overall_status: AvailabilityStatus = AvailabilityStatus.HEALTHY

    @property
    def cpu_summary(self) -> str:
        """Resumo textual do estado do CPU."""
        freq = ""
        if self.cpu.frequency_current_mhz:
            freq = f" @ {self.cpu.frequency_current_mhz:.0f}MHz"
        return f"CPU {self.cpu.percent:.1f}% ({self.cpu.count} cores){freq}"

    @property
    def memory_summary(self) -> str:
        """Resumo textual da utilização de memória."""
        return (
            f"{self.memory.used_gb:.1f}/{self.memory.total_gb:.1f}GB "
            f"({self.memory.percent:.1f}%)"
        )

    @property
    def uptime_summary(self) -> str:
        """Resumo textual do uptime."""
        if self.uptime is None:
            return "Uptime desconhecido"
        h = self.uptime.uptime_hours
        if h < 24:
            return f"{h:.1f} horas"
        d = self.uptime.uptime_days
        return f"{d:.1f} dias"

    @property
    def availability_summary(self) -> str:
        """Resumo textual da disponibilidade efectiva global."""
        return f"Disponibilidade {self.overall_status.value.upper()}"

    @property
    def top_process(self) -> ProcessInfo | None:
        """O processo que consome mais memória RSS, se existir."""
        if not self.processes:
            return None
        return max(self.processes, key=lambda p: p.memory_rss_bytes)

    def get_availability(self, domain: AvailabilityDomain) -> RuntimeAvailability | None:
        """Obtém a disponibilidade para um domínio específico."""
        for avail in self.availability:
            if avail.domain == domain:
                return avail
        return None

    @property
    def cpu_availability(self) -> RuntimeAvailability | None:
        """Disponibilidade efectiva de processamento."""
        return self.get_availability(AvailabilityDomain.CPU)

    @property
    def memory_availability(self) -> RuntimeAvailability | None:
        """Disponibilidade efectiva de memória."""
        return self.get_availability(AvailabilityDomain.MEMORY)


class RuntimeDiscoverer(Protocol):
    """Protocolo para descoberta de estado de runtime.

    Cada implementação concreta (genérica psutil, ou futuras
    Windows/Linux específicas) deve cumprir este contrato.
    """

    def discover_cpu_load(self) -> CpuLoad:
        """Descobre o estado actual de carga do CPU."""
        ...

    def discover_memory(self) -> MemoryRuntime:
        """Descobre a utilização actual de memória."""
        ...

    def discover_uptime(self) -> SystemUptime | None:
        """Descobre o tempo de actividade do sistema."""
        ...

    def discover_all(self) -> RuntimeProfile:
        """Descobre e agrega todo o perfil de runtime."""
        ...
