"""Testes da monitorização contínua do Runtime Engine.

Valida a unidade residual da Fase 8 que complementa a observabilidade
pós-facto (``ExecutionReport``/``SchedulerReport``) com observação **durante**
a execução: o ``ExecutionMonitor`` regista o estado em curso de cada
execução e de cada agendamento e expõe ``snapshot()`` seguro para leitura
de outra thread.

A integração é aditiva: sem ``monitor``, o ``RuntimeManager`` e o
``Scheduler`` comportam-se exactamente como antes (regressão coberta pela
suíte da 8.5). Estes testes verificam a fotografia em curso, o avanço entre
passos, a finalização (sucesso, falha, negação de política) e a propagação
pelo scheduler.
"""

import threading

from wsai2.core import CancellationToken, ExecutionContext, ExecutionPriority
from wsai2.core.errors import PermissionError, WsaiError
from wsai2.runtime_engine import (
    ExecutionMonitor,
    ExecutionSnapshot,
    ExecutionStatus,
    MonitorSnapshot,
    RuntimeManager,
    Scheduler,
    StepStatus,
)
from wsai2.security import PolicyEngine
from wsai2.task import ExecutionPlan


def _plano(
    task_id: str = "t-1",
    steps: tuple[str, ...] = ("preparar", "executar", "finalizar"),
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


def test_api_publica_exposta() -> None:
    """O monitor e as fotos são alcançáveis na API pública do subsistema."""
    from wsai2.runtime_engine import __all__

    assert "ExecutionMonitor" in __all__
    assert "ExecutionSnapshot" in __all__
    assert "MonitorSnapshot" in __all__


def test_monitor_comeca_vazio() -> None:
    """Um monitor novo não tem execuções nem agendamentos."""
    foto = ExecutionMonitor().snapshot()
    assert isinstance(foto, MonitorSnapshot)
    assert foto.running == ()
    assert foto.finished == ()
    assert foto.started == 0
    assert foto.completed == 0
    assert foto.schedule_started_at is None
    assert foto.last_schedule is None


def test_monitor_observa_execucao_em_curso() -> None:
    """Enquanto o plano corre, a fotografia revela a execução in-flight."""
    monitor = ExecutionMonitor()
    iniciado = threading.Event()
    soltar = threading.Event()

    def runner(indice: int, passo: str) -> None:
        if indice == 0:
            iniciado.set()
            assert soltar.wait(timeout=5)

    gestor = RuntimeManager()
    resultado: dict[str, object] = {}

    def executar() -> None:
        resultado["report"] = gestor.execute_plan(
            _plano(),
            step_runner=runner,
            monitor=monitor,
        )

    thread = threading.Thread(target=executar)
    thread.start()
    assert iniciado.wait(timeout=5)

    foto = monitor.snapshot()
    assert len(foto.running) == 1
    em_curso = foto.running[0]
    assert isinstance(em_curso, ExecutionSnapshot)
    assert em_curso.running is True
    assert em_curso.task_id == "t-1"
    assert em_curso.execution_id == "exec-t-1"
    assert em_curso.current_step == 0
    assert em_curso.current_step_name == "preparar"
    assert em_curso.elapsed >= 0.0
    assert foto.started == 1
    assert foto.completed == 0
    assert foto.finished == ()

    soltar.set()
    thread.join(timeout=5)
    assert thread.is_alive() is False

    relatorio = resultado["report"]
    assert relatorio.is_success is True  # type: ignore[union-attr]
    fim = monitor.snapshot()
    assert fim.running == ()
    assert fim.completed == 1
    assert fim.finished[0].execution_id == "exec-t-1"


def test_monitor_acompanha_avancado_de_passos() -> None:
    """O passo actual avança entre leituras e o tempo decorre."""
    monitor = ExecutionMonitor()
    no_pass0 = threading.Event()
    no_pass1 = threading.Event()
    soltar0 = threading.Event()
    soltar1 = threading.Event()

    def runner(indice: int, passo: str) -> None:
        if indice == 0:
            no_pass0.set()
            assert soltar0.wait(timeout=5)
        elif indice == 1:
            no_pass1.set()
            assert soltar1.wait(timeout=5)

    gestor = RuntimeManager()
    thread = threading.Thread(
        target=lambda: gestor.execute_plan(
            _plano(),
            step_runner=runner,
            monitor=monitor,
        )
    )
    thread.start()

    assert no_pass0.wait(timeout=5)
    primeiro = monitor.snapshot().running[0]
    assert primeiro.current_step == 0

    soltar0.set()
    assert no_pass1.wait(timeout=5)
    segundo = monitor.snapshot().running[0]
    assert segundo.current_step == 1
    assert segundo.current_step_name == "executar"
    assert segundo.elapsed >= primeiro.elapsed

    soltar1.set()
    thread.join(timeout=5)
    assert thread.is_alive() is False
    assert monitor.snapshot().running == ()


def test_monitor_regista_falha_de_passo() -> None:
    """Uma falha de passo termina a execução e o relatório é retido."""
    monitor = ExecutionMonitor()

    def runner(indice: int, passo: str) -> None:
        if indice == 1:
            raise RuntimeError("falha simulada")

    relatorio = RuntimeManager().execute_plan(
        _plano(),
        step_runner=runner,
        monitor=monitor,
    )

    assert relatorio.status is ExecutionStatus.FAILED
    foto = monitor.snapshot()
    assert foto.running == ()
    assert foto.started == 1
    assert foto.completed == 1
    assert foto.finished[0].task_id == "t-1"
    assert isinstance(foto.finished[0].error, WsaiError)


def test_monitor_cobre_execucoes_negadas_por_politica() -> None:
    """Mesmo uma execução negada pela política é finalizada e observada."""
    monitor = ExecutionMonitor()
    motor = PolicyEngine({"alice": ("outra.acao",)})
    contexto = ExecutionContext(
        execution_id="exec-alice",
        task_id="t-1",
        principal="alice",
        project_id="proj-1",
        priority=ExecutionPriority.NORMAL,
        cancellation=CancellationToken(),
    )

    relatorio = RuntimeManager().execute_plan(
        _plano(),
        context=contexto,
        policy=motor,
        monitor=monitor,
    )

    assert isinstance(relatorio.error, PermissionError)
    assert relatorio.steps != ()
    assert all(p.status is StepStatus.SKIPPED for p in relatorio.steps)
    foto = monitor.snapshot()
    assert foto.started == 1
    assert foto.completed == 1
    assert foto.running == ()


def test_monitor_reutiliza_relatorios_finais() -> None:
    """O monitor expõe o próprio ExecutionReport produzido pelo gestor."""
    monitor = ExecutionMonitor()
    registo: list[str] = []

    def runner(indice: int, passo: str) -> None:
        registo.append(passo)

    relatorio = RuntimeManager().execute_plan(
        _plano(),
        step_runner=runner,
        monitor=monitor,
    )

    fim = monitor.snapshot()
    assert fim.finished[0] == relatorio
    assert fim.finished[0].steps == relatorio.steps


def test_scheduler_propaga_monitorizacao() -> None:
    """O scheduler alimenta o monitor e retém o relatório de agendamento."""
    monitor = ExecutionMonitor()
    gestor = RuntimeManager()

    relatorio = Scheduler(gestor).run(
        (_plano(task_id="t1", steps=("a",)), _plano(task_id="t2", steps=("a",))),
        monitor=monitor,
    )

    assert relatorio.order == ("t1", "t2")
    foto = monitor.snapshot()
    assert foto.running == ()
    assert foto.started == 2
    assert foto.completed == 2
    assert foto.schedule_started_at is None
    assert foto.last_schedule is not None
    assert foto.last_schedule.order == ("t1", "t2")
    assert [r.task_id for r in foto.finished] == ["t1", "t2"]