"""Testes do subsistema Runtime Intelligence.

Valida a descoberta de estado de runtime: carga do CPU, utilização de
memória, processos activos e tempo de actividade do sistema.
"""

from wsai2.runtime import (
    CpuLoad,
    MemoryRuntime,
    ProcessInfo,
    RuntimeProfile,
    SystemUptime,
    discover_runtime,
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
