"""Testes da unidade residual 3 — filas multicamadas."""

import pytest

from wsai2.core.context import ExecutionPriority
from wsai2.core.errors import ValidationError
from wsai2.runtime_engine import MultilayerExecutionQueue
from wsai2.task import ExecutionPlan


def _plan(task_id: str) -> ExecutionPlan:
    return ExecutionPlan(
        task_id=task_id,
        category="chat",
        feasible=True,
        model_id="model",
        provider_id="provider",
        reasons=(),
        steps=("step",),
    )


def test_queue_prioriza_e_preserva_ordem_estavel() -> None:
    queue = MultilayerExecutionQueue[ExecutionPlan]()
    queue.enqueue(_plan("low"), ExecutionPriority.LOW)
    queue.enqueue(_plan("critical"), ExecutionPriority.CRITICAL)
    queue.enqueue(_plan("high"), ExecutionPriority.HIGH)

    assert [queue.pop_next().task_id for _ in range(3)] == ["critical", "high", "low"]
    assert queue.snapshot().total == 0


def test_queue_com_capacidade_preempta_pendente_de_menor_prioridade() -> None:
    queue = MultilayerExecutionQueue[ExecutionPlan](max_ready=2)
    low = _plan("low")
    normal = _plan("normal")
    critical = _plan("critical")

    queue.enqueue(low, ExecutionPriority.LOW)
    queue.enqueue(normal, ExecutionPriority.NORMAL)
    queue.enqueue(critical, ExecutionPriority.CRITICAL)

    assert queue.snapshot().ready == 2
    assert queue.snapshot().backlog == 1
    assert queue.pop_next() is critical
    assert queue.pop_next() is normal
    assert queue.pop_next() is low


def test_queue_nao_preempta_prioridade_superior_ja_pronta() -> None:
    queue = MultilayerExecutionQueue[ExecutionPlan](max_ready=1)
    critical = _plan("critical")
    low = _plan("low")

    queue.enqueue(critical, ExecutionPriority.CRITICAL)
    queue.enqueue(low, ExecutionPriority.LOW)

    assert queue.pop_next() is critical
    assert queue.pop_next() is low


def test_queue_pending_reflete_ordem_de_prioridade() -> None:
    queue = MultilayerExecutionQueue[ExecutionPlan](max_ready=1)
    low = _plan("low")
    high = _plan("high")
    queue.enqueue(low, ExecutionPriority.LOW)
    queue.enqueue(high, ExecutionPriority.HIGH)

    assert [plan.task_id for plan in queue.pending()] == ["high", "low"]


def test_queue_clear_remove_todos_os_pendentes() -> None:
    queue = MultilayerExecutionQueue[ExecutionPlan](max_ready=1)
    queue.enqueue(_plan("a"), ExecutionPriority.NORMAL)
    queue.enqueue(_plan("b"), ExecutionPriority.LOW)

    removed = queue.clear()

    assert [plan.task_id for plan in removed] == ["a", "b"]
    assert queue.snapshot().total == 0


def test_queue_rejeita_capacidade_invalida() -> None:
    with pytest.raises(ValidationError, match="max_ready"):
        MultilayerExecutionQueue(max_ready=0)


def test_queue_run_directo_do_scheduler_eh_preservado_sem_queue() -> None:
    """Contrato de regressão: queue=None não altera a via histórica."""
    from wsai2.runtime_engine import RuntimeManager, Scheduler

    manager = RuntimeManager()
    scheduler = Scheduler(manager)
    plans = [_plan("b"), _plan("a")]

    report = scheduler.run(
        plans,
        priorities={"a": ExecutionPriority.CRITICAL, "b": ExecutionPriority.LOW},
    )

    assert report.order == ("a", "b")


def test_scheduler_pode_consumir_fila_multicamada() -> None:
    from wsai2.runtime_engine import RuntimeManager, Scheduler

    queue = MultilayerExecutionQueue[ExecutionPlan](max_ready=1)
    scheduler = Scheduler(RuntimeManager())
    plans = [_plan("low"), _plan("critical"), _plan("normal")]

    report = scheduler.run(
        plans,
        priorities={
            "low": ExecutionPriority.LOW,
            "critical": ExecutionPriority.CRITICAL,
            "normal": ExecutionPriority.NORMAL,
        },
        queue=queue,
    )

    assert report.order == ("critical", "normal", "low")
    assert queue.snapshot().total == 0
