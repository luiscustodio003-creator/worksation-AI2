"""Testes da concorrência entre planos do Runtime Engine.

Valida a unidade residual 2 da Fase 8: o ``Scheduler`` executa planos em
paralelo (``concurrency > 1``) de forma **aditiva e opcional**, preservando
o agendamento sequencial por prioridade por omissão (``concurrency == 1``).

Cobre: validação do parâmetro; equivalência com o caminho sequencial;
execução paralela real (sobreposição com barrier); ordem de prioridade no
relatório; ``stop_on_failure`` com pendentes descartados; monitorização e
governação de recursos partilhada em execução paralela; unicidade dos
``execution_id``.
"""

import threading
import time

import pytest

from wsai2.core import ExecutionContext, ExecutionPriority, ValidationError
from wsai2.extension import ResourceLimit
from wsai2.hardware import (
    Architecture,
    CpuInfo,
    CpuVendor,
    HardwareProfile,
    MemoryInfo,
    StorageInfo,
)
from wsai2.resource import ResourceGovernor
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile
from wsai2.runtime_engine import ExecutionMonitor, ExecutionStatus, RuntimeManager, Scheduler
from wsai2.task import ExecutionPlan

_GB = 1024 ** 3


def _plano(
    task_id: str = "t-1",
    steps: tuple[str, ...] = ("a", "b"),
) -> ExecutionPlan:
    """Constrói um ExecutionPlan de teste executável."""
    return ExecutionPlan(
        task_id=task_id,
        category="chat",
        feasible=True,
        model_id="modelo-teste",
        provider_id="fornecedor-teste",
        reasons=(),
        steps=steps,
    )


def _hardware(ram_gb: float = 16.0, cores: int = 8) -> HardwareProfile:
    """Constrói um HardwareProfile de teste com RAM folgada."""
    return HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL,
            model_name="CPU de Teste",
            architecture=Architecture.X86_64,
            physical_cores=cores,
            logical_cores=cores * 2,
        ),
        memory=MemoryInfo(total_bytes=int(ram_gb * _GB)),
        gpus=(),
        storage=(
            StorageInfo(
                device_path="C:",
                total_bytes=500 * _GB,
                type="ssd",
                mount_point="C:",
            ),
        ),
    )


def _runtime(ram_gb: float = 16.0, available_gb: float = 6.0) -> RuntimeProfile:
    """Constrói um RuntimeProfile de teste com folga de memória."""
    used = ram_gb - available_gb
    return RuntimeProfile(
        cpu=CpuLoad(percent=30.0, per_core=(), count=8),
        memory=MemoryRuntime(
            total_bytes=int(ram_gb * _GB),
            available_bytes=int(available_gb * _GB),
            used_bytes=int(used * _GB),
            percent=(used / ram_gb) * 100.0,
        ),
    )


def test_scheduler_rejeita_concurrency_invalida() -> None:
    """Um 'concurrency' inválido é rejeitado antes de qualquer execução."""
    for invalido in (0, -1, True, "2"):
        with pytest.raises(ValidationError) as exc:
            Scheduler(RuntimeManager()).run(
                (_plano(task_id="p1", steps=("a",)),),
                concurrency=invalido,  # type: ignore[arg-type]
            )
        assert exc.value.code == "wsai.runtime.concurrency"


def test_scheduler_concurrency_um_preserva_sequencial() -> None:
    """Com 'concurrency=1' o comportamento é idêntico ao sequencial."""
    gestor = RuntimeManager()
    planos = (
        _plano(task_id="p1", steps=("a",)),
        _plano(task_id="p2", steps=("a",)),
        _plano(task_id="p3", steps=("a",)),
    )
    por_defeito = Scheduler(gestor).run(planos)
    explicito = Scheduler(gestor).run(planos, concurrency=1)

    assert explicito.order == por_defeito.order == ("p1", "p2", "p3")
    assert explicito.total == explicito.succeeded == 3
    assert explicito.failed == 0


def test_scheduler_concorrencia_executa_todos_os_planos() -> None:
    """Em paralelo, todos os planos executam e a ordem preserva prioridade."""
    planos = (
        _plano(task_id="baixa", steps=("a",)),
        _plano(task_id="critica", steps=("a",)),
        _plano(task_id="normal", steps=("a",)),
        _plano(task_id="media", steps=("a",)),
        _plano(task_id="lenta", steps=("a",)),
    )
    relatorio = Scheduler(RuntimeManager()).run(
        planos,
        priorities={
            "baixa": ExecutionPriority.LOW,
            "critica": ExecutionPriority.CRITICAL,
            "normal": ExecutionPriority.NORMAL,
            "media": ExecutionPriority.HIGH,
            "lenta": ExecutionPriority.LOW,
        },
        concurrency=3,
    )

    assert relatorio.total == 5
    assert relatorio.succeeded == 5
    assert relatorio.failed == 0
    assert [o.task_id for o in relatorio.outcomes] == list(relatorio.order)
    assert relatorio.order == ("critica", "media", "normal", "baixa", "lenta")
    assert [o.priority for o in relatorio.outcomes][:3] == [
        ExecutionPriority.CRITICAL,
        ExecutionPriority.HIGH,
        ExecutionPriority.NORMAL,
    ]


def test_scheduler_concorrencia_sobrepoe_execucoes() -> None:
    """Com dois planos e dois workers, ambos decorrem em simultâneo.

    Usa uma barrier: dois planos só atravessam o passo se se encontrarem
    em execução ao mesmo tempo — prova de paralelismo real (em sequencial,
    o primeiro bloquearia na barrier).
    """
    encontro = threading.Barrier(2)

    def runner(indice: int, passo: str) -> None:
        encontro.wait(timeout=5)

    relatorio = Scheduler(RuntimeManager()).run(
        (_plano(task_id="p1", steps=("único",)), _plano(task_id="p2", steps=("único",))),
        step_runner=runner,
        concurrency=2,
    )

    assert relatorio.total == 2
    assert relatorio.succeeded == 2
    assert relatorio.order == ("p1", "p2")


def test_scheduler_concorrencia_stop_on_failure_descarta_pendentes() -> None:
    """Uma falha com 'stop_on_failure' descarta os planos ainda não iniciados.

    O plano de falha aguarda o sinal de que o plano longo já está em
    execução (determinístico): a falha assinala o evento de paragem depois
    de o longo ter começado; os planos ainda na fila não são iniciados e
    não entram no relatório.
    """
    lento_iniciado = threading.Event()

    def runner(indice: int, passo: str) -> None:
        if passo == "falha":
            assert lento_iniciado.wait(timeout=5)
            raise RuntimeError("falha simulada")
        if passo == "lento":
            lento_iniciado.set()
            time.sleep(0.5)

    relatorio = Scheduler(RuntimeManager()).run(
        (
            _plano(task_id="falha", steps=("falha",)),
            _plano(task_id="lento", steps=("lento",)),
            _plano(task_id="p3", steps=("a",)),
            _plano(task_id="p4", steps=("a",)),
        ),
        step_runner=runner,
        concurrency=2,
        stop_on_failure=True,
    )

    assert relatorio.total == 2
    assert relatorio.order == ("falha", "lento")
    assert relatorio.failed == 1
    assert relatorio.succeeded == 1


def test_scheduler_concorrencia_falha_parcial_sem_stop() -> None:
    """Sem 'stop_on_failure', a falha de um plano não impede os restantes."""
    planos = (
        _plano(task_id="p1", steps=("a",)),
        _plano(task_id="falha", steps=("falha",)),
        _plano(task_id="p3", steps=("a",)),
    )

    def runner(indice: int, passo: str) -> None:
        if passo == "falha":
            raise RuntimeError("falha simulada")

    relatorio = Scheduler(RuntimeManager()).run(planos, step_runner=runner, concurrency=2)

    assert relatorio.total == 3
    assert relatorio.failed == 1
    assert relatorio.succeeded == 2
    assert [o.task_id for o in relatorio.outcomes if o.report.is_success] == ["p1", "p3"]


def test_scheduler_concorrencia_monitor_observa_todos() -> None:
    """O monitor regista todas as execuções paralelas e o agendamento."""
    monitor = ExecutionMonitor()
    planos = (
        _plano(task_id="p1", steps=("a",)),
        _plano(task_id="p2", steps=("b",)),
        _plano(task_id="p3", steps=("c",)),
        _plano(task_id="p4", steps=("d",)),
    )

    relatorio = Scheduler(RuntimeManager()).run(planos, concurrency=2, monitor=monitor)

    assert relatorio.total == 4
    foto = monitor.snapshot()
    assert foto.running == ()
    assert foto.started == 4
    assert foto.completed == 4
    assert {r.task_id for r in foto.finished} == {p.task_id for p in planos}
    assert foto.last_schedule is not None
    assert foto.last_schedule.order == ("p1", "p2", "p3", "p4")


def _com_contexto_de_recurso(plano: ExecutionPlan) -> ExecutionContext:
    """Contexto com um budget pequeno de RAM para o teste de governação."""
    return ExecutionContext(
        execution_id=f"exec-{plano.task_id}",
        task_id=plano.task_id,
        budget=(ResourceLimit(name="ram", value=0.5),),
    )


def test_scheduler_concorrencia_governador_partilhado_seguro() -> None:
    """Planos paralelos sobre o mesmo governador reservam/libertam sem perdas."""
    governador = ResourceGovernor(hardware=_hardware(), runtime=_runtime())
    gestor = RuntimeManager(governor=governador)
    planos = tuple(_plano(task_id=f"g{i}", steps=("a",)) for i in range(8))

    relatorio = Scheduler(gestor).run(
        planos,
        concurrency=4,
        context_factory=_com_contexto_de_recurso,
    )

    assert relatorio.total == 8
    assert relatorio.succeeded == 8
    assert governador.outstanding == ()
    assert all(o.report.execution_id.startswith("exec-") for o in relatorio.outcomes)


def test_scheduler_concorrencia_rejeita_execution_ids_duplicados() -> None:
    """Em paralelo, execution_ids duplicados são rejeitados antes de executar."""

    def factory(plano: ExecutionPlan) -> ExecutionContext:
        return ExecutionContext(execution_id="duplicado", task_id=plano.task_id)

    with pytest.raises(ValidationError) as exc:
        Scheduler(RuntimeManager()).run(
            (_plano(task_id="p1", steps=("a",)), _plano(task_id="p2", steps=("a",))),
            concurrency=2,
            context_factory=factory,
        )
    assert exc.value.code == "wsai.runtime.duplicate_execution"


def test_scheduler_concorrencia_contextos_unicos_por_omissao() -> None:
    """Sem factory, os execution_ids dos planos paralelos são únicos."""
    relatorio = Scheduler(RuntimeManager()).run(
        (_plano(task_id="p1", steps=("a",)), _plano(task_id="p2", steps=("a",))),
        concurrency=2,
    )

    ids = [o.report.execution_id for o in relatorio.outcomes]
    assert len(set(ids)) == 2
    assert all(i.startswith("exec-") for i in ids)
    assert all(o.report.status is ExecutionStatus.SUCCESS for o in relatorio.outcomes)