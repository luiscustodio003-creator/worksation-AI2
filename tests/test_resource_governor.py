"""Testes da Governação de Recursos (Fase 8.3).

Valida o governador de recursos: normalização de limites declarativos,
veredictos por dimensão (RAM, CPU, VRAM, disco, não reconhecido),
validação de orçamentos contra perfis estruturais/runtime e o accounting
de alocações (reserva, sobre-compromisso, libertação).
"""

import pytest

from wsai2.core.errors import ResourceError
from wsai2.extension import ResourceLimit
from wsai2.hardware import (
    Architecture,
    CpuInfo,
    CpuVendor,
    GpuInfo,
    HardwareProfile,
    MemoryInfo,
    StorageInfo,
)
from wsai2.resource import (
    AllocationState,
    ResourceDimension,
    ResourceGovernor,
    ResourceVerdict,
)
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile

_GB = 1024 ** 3


def _hardware(
    ram_gb: float = 16.0,
    cores: int = 8,
    vram_gb: float | None = None,
    storage_gb: float = 500.0,
) -> HardwareProfile:
    """Constrói um HardwareProfile de teste."""
    gpus = ()
    if vram_gb:
        gpus = (
            GpuInfo(name="GPU Teste", vendor="nvidia", vram_bytes=int(vram_gb * _GB)),
        )
    return HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL,
            model_name="CPU de Teste",
            architecture=Architecture.X86_64,
            physical_cores=cores,
            logical_cores=cores * 2,
        ),
        memory=MemoryInfo(total_bytes=int(ram_gb * _GB)),
        gpus=gpus,
        storage=(
            StorageInfo(
                device_path="C:",
                total_bytes=int(storage_gb * _GB),
                type="ssd",
                mount_point="C:",
            ),
        ),
    )


def _runtime(
    ram_gb: float = 16.0,
    available_gb: float = 6.0,
    cpu_percent: float = 30.0,
    cpu_count: int = 8,
) -> RuntimeProfile:
    """Constrói um RuntimeProfile de teste."""
    used = ram_gb - available_gb
    percent = (used / ram_gb) * 100.0 if ram_gb else 0.0
    return RuntimeProfile(
        cpu=CpuLoad(percent=cpu_percent, per_core=(), count=cpu_count),
        memory=MemoryRuntime(
            total_bytes=int(ram_gb * _GB),
            available_bytes=int(available_gb * _GB),
            used_bytes=int(used * _GB),
            percent=percent,
        ),
    )


def _governador(**kwargs: object) -> ResourceGovernor:
    """Constrói um governador de teste."""
    return ResourceGovernor(hardware=_hardware(), runtime=_runtime())


def test_orcamento_vazio_satisfeito_por_vacuidade() -> None:
    """Um orçamento sem limites deve ser satisfeito."""
    resultado = _governador().evaluate(())
    assert resultado.is_available is True
    assert resultado.checks == ()


def test_limite_memory_mb_normalizado_para_gb() -> None:
    """Um limite em MB deve ser normalizado para gigabytes."""
    resultado = _governador().evaluate((ResourceLimit(name="memory_mb", value=512.0),))
    check = resultado.checks[0]
    assert check.dimension is ResourceDimension.RAM
    assert check.required == pytest.approx(0.5)
    assert check.capacity == pytest.approx(16.0)
    assert check.available_now == pytest.approx(6.0)


def test_ram_suficiente_verdict_available() -> None:
    """RAM disponível igual ou superior ao pedido deve ser satisfeita."""
    resultado = _governador().evaluate((ResourceLimit(name="ram_gb", value=2.0),))
    check = resultado.checks[0]
    assert check.satisfied is True
    assert check.verdict is ResourceVerdict.AVAILABLE


def test_ram_insuficiente_verdict_unavailable() -> None:
    """RAM disponível inferior ao pedido deve falhar a verificação."""
    resultado = _governador().evaluate((ResourceLimit(name="ram_gb", value=8.0),))
    check = resultado.checks[0]
    assert check.satisfied is False
    assert check.verdict is ResourceVerdict.UNAVAILABLE
    assert resultado.is_available is False


def test_cpu_cores_suficiente() -> None:
    """Núcleos livres derivados da carga devem satisfazer o pedido."""
    resultado = _governador().evaluate((ResourceLimit(name="cpu", value=2.0),))
    check = resultado.checks[0]
    assert check.dimension is ResourceDimension.CPU
    assert check.available_now == pytest.approx(5.6)  # 8 cores * (100-30)%
    assert check.satisfied is True


def test_cpu_cores_insuficiente_sob_carga() -> None:
    """Carga alta deve reduzir os núcleos livres efectivos."""
    governador = ResourceGovernor(
        hardware=_hardware(),
        runtime=_runtime(cpu_percent=90.0, cpu_count=8),
    )
    resultado = governador.evaluate((ResourceLimit(name="cpu_cores", value=6.0),))
    check = resultado.checks[0]
    assert check.available_now == pytest.approx(0.8)
    assert check.satisfied is False
    assert check.verdict is ResourceVerdict.UNAVAILABLE


def test_limite_nao_reconhecido() -> None:
    """Um nome de limite desconhecido deve ter veredicto explícito."""
    resultado = _governador().evaluate((ResourceLimit(name="servicos_exoticos", value=1.0),))
    check = resultado.checks[0]
    assert check.dimension is None
    assert check.satisfied is False
    assert check.verdict is ResourceVerdict.UNRECOGNIZED
    assert resultado.is_available is False
    assert len(resultado.unrecognized_checks) == 1


def test_vram_sem_gpu_governado_pela_capacidade() -> None:
    """VRAM exigida sem GPU presente deve falhar (capacidade zero)."""
    resultado = _governador().evaluate((ResourceLimit(name="vram_gb", value=4.0),))
    check = resultado.checks[0]
    assert check.dimension is ResourceDimension.VRAM
    assert check.capacity == 0.0
    assert check.available_now is None
    assert check.satisfied is False


def test_vram_com_gpu_suficiente() -> None:
    """VRAM exigida dentro da capacidade da GPU deve ser satisfeita."""
    governador = ResourceGovernor(
        hardware=_hardware(vram_gb=8.0),
        runtime=_runtime(),
    )
    resultado = governador.evaluate((ResourceLimit(name="vram_gb", value=4.0),))
    check = resultado.checks[0]
    assert check.capacity == pytest.approx(8.0)
    assert check.available_now is None
    assert check.satisfied is True


def test_disco_governado_pela_capacidade_estrutural() -> None:
    """Disco exigido dentro da capacidade total deve ser satisfeito."""
    resultado = _governador().evaluate((ResourceLimit(name="disk_gb", value=100.0),))
    check = resultado.checks[0]
    assert check.dimension is ResourceDimension.DISK
    assert check.available_now is None
    assert check.satisfied is True


def test_disco_acima_da_capacidade_insuficiente() -> None:
    """Disco exigido acima da capacidade total deve falhar."""
    resultado = _governador().evaluate((ResourceLimit(name="disk_mb", value=(600.0 * 1024)),))
    check = resultado.checks[0]
    assert check.satisfied is False


def test_limite_negativo_sem_pretensao() -> None:
    """Um limite negativo não deve constituir pretensão (valor nulo)."""
    resultado = _governador().evaluate((ResourceLimit(name="ram_gb", value=-5.0),))
    check = resultado.checks[0]
    assert check.required == 0.0
    assert check.satisfied is True


def test_orcamento_mistura_limites_com_falha() -> None:
    """Orçamento rejeitado deve listar as verificações em falha."""
    orcamento = (
        ResourceLimit(name="ram_gb", value=2.0),
        ResourceLimit(name="vram_gb", value=8.0),
        ResourceLimit(name="nome_desconhecido", value=1.0),
    )
    resultado = _governador().evaluate(orcamento)
    assert resultado.is_available is False
    assert len(resultado.unavailable_checks) == 2
    assert len(resultado.available_checks) == 1
    assert len(resultado.unrecognized_checks) == 1


def test_allocacao_reserva_e_contabiliza() -> None:
    """Alocar deve criar reserva e aumentar o valor comprometido."""
    governador = _governador()
    alocacao = governador.allocate("exec-1", (ResourceLimit(name="ram_gb", value=2.0),))
    assert alocacao.is_active is True
    assert alocacao.owner == "exec-1"
    assert governador.committed_for(ResourceDimension.RAM) == pytest.approx(2.0)
    assert len(governador.outstanding) == 1


def test_allocacao_sobre_compromisso_rejeitada() -> None:
    """Reservas sucessivas além da folga devem ser rejeitadas."""
    governador = _governador()
    governador.allocate("exec-1", (ResourceLimit(name="ram_gb", value=2.0),))
    with pytest.raises(ResourceError) as exc:
        governador.allocate("exec-2", (ResourceLimit(name="ram_gb", value=5.0),))
    assert exc.value.code == "wsai.resource.insufficient"
    assert len(governador.outstanding) == 1


def test_allocacao_nao_alterada_por_orcamento_insatisfeito() -> None:
    """Falha de alocação não deve deixar reservas no livro."""
    governador = _governador()
    with pytest.raises(ResourceError):
        governador.allocate("exec-1", (ResourceLimit(name="ram_gb", value=99.0),))
    assert len(governador.outstanding) == 0


def test_release_devolve_recursos() -> None:
    """Libertar deve retirar a reserva e devolver a folga anterior."""
    governador = _governador()
    alocacao = governador.allocate("exec-1", (ResourceLimit(name="ram_gb", value=4.0),))
    assert governador.committed_for(ResourceDimension.RAM) == pytest.approx(4.0)

    libertada = governador.release(alocacao.allocation_id)
    assert libertada.state is AllocationState.RELEASED
    assert libertada.is_active is False
    assert governador.committed_for(ResourceDimension.RAM) == pytest.approx(0.0)
    assert len(governador.outstanding) == 0

    nova = governador.allocate("exec-2", (ResourceLimit(name="ram_gb", value=5.0),))
    assert nova.is_active is True


def test_release_desconhecida_levanta() -> None:
    """Libertar uma alocação desconhecida deve lançar ResourceError."""
    with pytest.raises(ResourceError) as exc:
        _governador().release("exec:0")
    assert exc.value.code == "wsai.resource.unknown"


def test_release_idempotente() -> None:
    """Libertar uma alocação já libertada não deve lançar."""
    governador = _governador()
    alocacao = governador.allocate("exec-1", (ResourceLimit(name="ram_gb", value=1.0),))
    governador.release(alocacao.allocation_id)
    repetida = governador.release(alocacao.allocation_id)
    assert repetida.state is AllocationState.RELEASED
    assert len(governador.outstanding) == 0


def test_allocacao_com_id_explicito_e_duplicado() -> None:
    """Um id explícito pode ser usado, mas não duplicado."""
    governador = _governador()
    limite = (ResourceLimit(name="ram_gb", value=1.0),)
    governador.allocate("exec-1", limite, allocation_id="reserva-1")
    with pytest.raises(ResourceError) as exc:
        governador.allocate("exec-2", limite, allocation_id="reserva-1")
    assert exc.value.code == "wsai.resource.duplicate"


def test_orcamento_vazio_alocado_sem_pretensoes() -> None:
    """Alocar um orçamento vazio deve criar uma reserva de teste."""
    governador = _governador()
    alocacao = governador.allocate("exec-1", ())
    assert alocacao.is_active is True
    assert governador.committed_for(ResourceDimension.RAM) == pytest.approx(0.0)