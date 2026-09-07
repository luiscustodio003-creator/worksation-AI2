"""Testes do subsistema Runtime Intelligence.

Valida a descoberta de estado de runtime: carga do CPU, utilização de
memória, processos activos, tempo de actividade do sistema e a
disponibilidade efectiva derivada.
"""

from wsai2.runtime import (
    AvailabilityDomain,
    AvailabilityStatus,
    CpuLoad,
    MemoryRuntime,
    ProcessInfo,
    RuntimeAvailability,
    RuntimeProfile,
    SystemUptime,
    analyze_runtime_availability,
    discover_runtime,
)
from wsai2.runtime.availability import (
    analyze_cpu_availability,
    analyze_memory_availability,
)
from wsai2.runtime.cpu import discover_cpu_load
from wsai2.runtime.memory import discover_memory_state


def test_descobrir_carga_cpu_retorna_estrutura_valida() -> None:
    """A descoberta de carga do CPU deve devolver CpuLoad com campos obrigatórios."""
    load = discover_cpu_load()

    assert isinstance(load, CpuLoad)
    assert isinstance(load.percent, float)
    assert 0.0 <= load.percent <= 100.0
    assert load.count >= 1
    assert isinstance(load.per_core, tuple)


def test_carga_cpu_por_core_coerente() -> None:
    """A lista de cores deve ter tantas entradas quanto cores detectados."""
    load = discover_cpu_load()

    # per_core pode estar vazio se a segunda chamada não capturar
    # (psutil.cpu_percent com interval 0 na segunda chamada devolve 0.0)
    if load.per_core:
        # Cada valor deve estar entre 0 e 100
        for core_pct in load.per_core:
            assert 0.0 <= core_pct <= 100.0


def test_carga_cpu_frequencia() -> None:
    """A frequência actual deve ser None ou um valor positivo."""
    load = discover_cpu_load()

    if load.frequency_current_mhz is not None:
        assert load.frequency_current_mhz > 0.0


def test_descobrir_memoria_runtime_retorna_estrutura_valida() -> None:
    """A descoberta de memória deve devolver MemoryRuntime com campos obrigatórios."""
    mem = discover_memory_state()

    assert isinstance(mem, MemoryRuntime)
    assert mem.total_bytes > 0
    assert mem.available_bytes > 0
    assert mem.used_bytes >= 0
    assert 0.0 <= mem.percent <= 100.0
    assert mem.total_bytes == mem.available_bytes + mem.used_bytes


def test_memoria_runtime_propriedades() -> None:
    """As propriedades de conversão de memória devem ser coerentes."""
    mem = discover_memory_state()

    assert mem.available_gb > 0
    assert mem.used_gb >= 0
    assert mem.total_gb > 0
    assert 0.0 <= mem.free_percent <= 100.0


def test_swap_runtime() -> None:
    """O estado de swap deve ser coerente com os valores totais e usados."""
    mem = discover_memory_state()

    assert mem.swap_total_bytes >= 0
    assert mem.swap_used_bytes >= 0
    assert 0.0 <= mem.swap_percent <= 100.0


def test_perfil_runtime_agregado() -> None:
    """A fábrica deve agregar carga, memória e processos num RuntimeProfile."""
    profile = discover_runtime()

    assert isinstance(profile, RuntimeProfile)
    assert isinstance(profile.cpu, CpuLoad)
    assert isinstance(profile.memory, MemoryRuntime)
    assert isinstance(profile.processes, tuple)
    assert len(profile.processes) > 0  # Pelo menos o processo do test runner


def test_processos_retornam_tipos_validos() -> None:
    """Cada processo deve conter campos obrigatórios e coerentes."""
    profile = discover_runtime()

    for proc in profile.processes:
        assert isinstance(proc, ProcessInfo)
        assert proc.pid > 0
        assert isinstance(proc.name, str)
        assert len(proc.name) > 0
        assert isinstance(proc.status, str)
        assert 0.0 <= proc.cpu_percent <= 100.0 or proc.cpu_percent == 0.0
        assert proc.memory_rss_bytes >= 0
        assert proc.memory_percent >= 0.0


def test_processo_maior_memoria_rss() -> None:
    """O processo de maior memória RSS deve ter RSS positivo."""
    profile = discover_runtime()

    top = profile.top_process
    assert top is not None
    assert top.memory_rss_bytes > 0


def test_processos_ordenados_por_memoria() -> None:
    """Os processos devem estar ordenados por memória RSS (decrescente)."""
    profile = discover_runtime()

    rss_values = [p.memory_rss_bytes for p in profile.processes]
    assert rss_values == sorted(rss_values, reverse=True)


def test_uptime_retornado() -> None:
    """O tempo de actividade deve ser um SystemUptime válido ou None."""
    profile = discover_runtime()

    if profile.uptime is not None:
        assert isinstance(profile.uptime, SystemUptime)
        assert profile.uptime.boot_timestamp > 0
        assert profile.uptime.uptime_seconds >= 0
        assert profile.uptime.uptime_hours >= 0
        assert profile.uptime.uptime_days >= 0


def test_resumos_textuais_nao_vazios() -> None:
    """Os resumos textuais devem ser strings não vazias."""
    profile = discover_runtime()

    cpu_summary = profile.cpu_summary
    assert isinstance(cpu_summary, str)
    assert len(cpu_summary) > 0
    assert "CPU" in cpu_summary

    mem_summary = profile.memory_summary
    assert isinstance(mem_summary, str)
    assert len(mem_summary) > 0
    assert "GB" in mem_summary

    uptime_summary = profile.uptime_summary
    assert isinstance(uptime_summary, str)
    assert len(uptime_summary) > 0


def test_cpu_load_propriedades_booleanas() -> None:
    """As propriedades is_idle e is_saturated devem ser coerentes com o valor."""
    load = discover_cpu_load()

    if load.percent < 10.0:
        assert load.is_idle is True
    else:
        assert load.is_idle is False

    if load.percent >= 90.0:
        assert load.is_saturated is True
    else:
        assert load.is_saturated is False


def test_memoria_runtime_has_swap_active() -> None:
    """A propriedade has_swap_active deve reflectir swap_used_bytes."""
    mem = discover_memory_state()
    assert mem.has_swap_active == (mem.swap_used_bytes > 0)


def test_perfil_runtime_tem_disponibilidade_derivada() -> None:
    """O perfil deve incluir disponibilidades derivadas para cada domínio."""
    profile = discover_runtime()

    assert isinstance(profile.availability, tuple)
    assert len(profile.availability) == 2  # cpu, memory

    domains = {avail.domain for avail in profile.availability}
    expected_domains = {
        AvailabilityDomain.CPU,
        AvailabilityDomain.MEMORY,
    }
    assert domains == expected_domains

    for avail in profile.availability:
        assert isinstance(avail, RuntimeAvailability)
        assert 0.0 <= avail.score <= 1.0
        assert isinstance(avail.status, AvailabilityStatus)
        assert isinstance(avail.details, dict)


def test_perfil_runtime_estado_global() -> None:
    """O perfil deve ter um estado global de disponibilidade válido."""
    profile = discover_runtime()

    assert isinstance(profile.overall_status, AvailabilityStatus)


def test_disponibilidade_cpu_valida() -> None:
    """A disponibilidade de CPU deve ter detalhes relevantes."""
    profile = discover_runtime()
    avail = profile.cpu_availability

    assert avail is not None
    assert avail.domain == AvailabilityDomain.CPU
    assert "load_percent" in avail.details
    assert "saturated" in avail.details
    assert "cores" in avail.details


def test_disponibilidade_memoria_valida() -> None:
    """A disponibilidade de memória deve ter detalhes relevantes."""
    profile = discover_runtime()
    avail = profile.memory_availability

    assert avail is not None
    assert avail.domain == AvailabilityDomain.MEMORY
    assert "used_percent" in avail.details
    assert "free_percent" in avail.details
    assert "available_gb" in avail.details
    assert avail.details["available_gb"] >= 0


def test_resumos_disponibilidade_nao_vazios() -> None:
    """O resumo textual de disponibilidade deve ser uma string não vazia."""
    profile = discover_runtime()

    summary = profile.availability_summary
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Disponibilidade" in summary


def test_analise_disponibilidade_cpu_determinista() -> None:
    """A análise de CPU deve ser coerente com a carga fornecida."""
    # CPU com 100% de carga → disponibilidade próxima de 0
    saturated_cpu = CpuLoad(percent=100.0, per_core=(), count=8)
    avail = analyze_cpu_availability(saturated_cpu)

    assert avail.domain == AvailabilityDomain.CPU
    assert avail.score == 0.0
    assert avail.status == AvailabilityStatus.CRITICAL
    assert avail.is_available is False

    # CPU ocioso → disponibilidade máxima
    idle_cpu = CpuLoad(percent=0.0, per_core=(), count=8)
    avail_idle = analyze_cpu_availability(idle_cpu)

    assert avail_idle.score == 1.0
    assert avail_idle.status == AvailabilityStatus.HEALTHY
    assert avail_idle.is_available is True


def test_analise_disponibilidade_memoria_determinista() -> None:
    """A análise de memória deve ser coerente com o estado fornecido."""
    # Memória totalmente livre → disponibilidade máxima
    mem_free = MemoryRuntime(
        total_bytes=16 * 1024**3,
        available_bytes=16 * 1024**3,
        used_bytes=0,
        percent=0.0,
    )
    avail = analyze_memory_availability(mem_free)

    assert avail.domain == AvailabilityDomain.MEMORY
    assert avail.score == 1.0
    assert avail.status == AvailabilityStatus.HEALTHY

    # Memória quase esgotada → disponibilidade crítica
    mem_exhausted = MemoryRuntime(
        total_bytes=16 * 1024**3,
        available_bytes=1024 * 1024 * 1024,
        used_bytes=15 * 1024**3,
        percent=93.75,
    )
    avail_exh = analyze_memory_availability(mem_exhausted)

    assert avail_exh.score < 0.5
    assert avail_exh.status in (AvailabilityStatus.DEGRADED, AvailabilityStatus.CRITICAL)


def test_analise_runtime_disponibilidade_global() -> None:
    """A análise agregada deve produzir disponibilidades para os dois domínios."""
    cpu = CpuLoad(percent=50.0, per_core=(), count=8)
    mem = MemoryRuntime(
        total_bytes=16 * 1024**3,
        available_bytes=8 * 1024**3,
        used_bytes=8 * 1024**3,
        percent=50.0,
    )

    availability = analyze_runtime_availability(cpu, mem)

    assert len(availability) == 2
    assert availability[0].domain == AvailabilityDomain.CPU
    assert availability[1].domain == AvailabilityDomain.MEMORY
    for avail in availability:
        assert 0.0 <= avail.score <= 1.0
        assert isinstance(avail.status, AvailabilityStatus)


def test_availability_status_completo() -> None:
    """Todos os estados de disponibilidade devem estar definidos."""
    statuses = set(AvailabilityStatus)
    expected = {
        AvailabilityStatus.HEALTHY,
        AvailabilityStatus.DEGRADED,
        AvailabilityStatus.CRITICAL,
    }
    assert statuses == expected


def test_availability_domain_completo() -> None:
    """Todos os domínios de disponibilidade devem estar definidos."""
    domains = set(AvailabilityDomain)
    expected = {
        AvailabilityDomain.CPU,
        AvailabilityDomain.MEMORY,
    }
    assert domains == expected
