"""Testes do Runtime Engine — gestor de execução e scheduler (Fase 8.5).

Valida o subsistema `wsai2.runtime_engine`: execução de planos
(`ExecutionPlan` da Fase 7) com as políticas centralizadas (timeout,
cancelamento, recuperação, orçamento de recursos) e o agendamento
determinístico por prioridade com relatório agregado.
"""

import time

import pytest

from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.core import (
    CancellationError,
    CancellationToken,
    ExecutionContext,
    ExecutionPriority,
    ValidationError,
)
from wsai2.core.errors import ExecutionError, ProviderError, ResourceError, WsaiError
from wsai2.execution import RecoveryPolicy, TimeoutPolicy
from wsai2.hardware import (
    Architecture,
    CpuInfo,
    CpuVendor,
    GpuInfo,
    HardwareProfile,
    MemoryInfo,
    StorageInfo,
)
from wsai2.model import create_default_registry as create_model_registry
from wsai2.provider import ProviderHealth, ProviderHealthStatus
from wsai2.resource import ResourceGovernor
from wsai2.runtime_engine import (
    ExecutionReport,
    ExecutionStatus,
    RuntimeManager,
    ScheduleOutcome,
    Scheduler,
    SchedulerReport,
    StepOutcome,
    StepStatus,
)
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile
from wsai2.task import ExecutionPlan, Task, TaskKind, build_execution_plan
from wsai2.extension import ResourceLimit

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


def _plano(
    task_id: str = "task-1",
    steps: tuple[str, ...] = ("preparar", "executar", "finalizar"),
    feasible: bool = True,
    model_id: str | None = "llama-teste",
    provider_id: str | None = "ollama",
    reasons: tuple[str, ...] = (),
) -> ExecutionPlan:
    """Constrói um ExecutionPlan de teste."""
    return ExecutionPlan(
        task_id=task_id,
        category="chat",
        feasible=feasible,
        model_id=model_id,
        provider_id=provider_id,
        reasons=reasons,
        steps=steps,
    )


def _contexto(**kwargs: object) -> ExecutionContext:
    """Constrói um contexto de execução de teste com valores válidos."""
    valores: dict[str, object] = {"execution_id": "exec-1", "task_id": "task-1"}
    valores.update(kwargs)
    return ExecutionContext(**valores)  # type: ignore[arg-type]


def _governador(**kwargs: object) -> ResourceGovernor:
    """Constrói um governador de teste."""
    return ResourceGovernor(hardware=_hardware(), runtime=_runtime())


def _fornecedor_saudavel(
    capabilities: tuple[str, ...],
) -> tuple[ProviderHealth, ...]:
    """Constrói um health check saudável para o fornecedor do plano."""
    return (
        ProviderHealth(
            provider_id="ollama",
            name="Ollama",
            base_url="http://localhost:11434",
            status=ProviderHealthStatus.HEALTHY,
            model_count=1,
            capabilities_provided=capabilities,
        ),
    )


# --- Gestor: validação -----------------------------------------------------


def test_gestor_rejeita_entrada_que_nao_e_plano() -> None:
    """Um argumento que não seja um plano deve ser rejeitado."""
    with pytest.raises(ValidationError) as exc:
        RuntimeManager().execute_plan(Task(id="t-1", kind=TaskKind.CHAT, prompt="oi"))
    assert exc.value.code == "wsai.execution.plan"


def test_gestor_rejeita_plano_nao_executavel() -> None:
    """Um plano infeasível (sem modelo ou fornecedor) deve ser rejeitado."""
    plano = _plano(
        feasible=False,
        model_id=None,
        provider_id=None,
        reasons=("faltam capacidades",),
    )
    with pytest.raises(ExecutionError) as exc:
        RuntimeManager().execute_plan(plano)
    assert exc.value.code == "wsai.execution.not_executable"


def test_gestor_rejeita_contexto_de_outra_tarefa() -> None:
    """Executar um plano num contexto de outra tarefa deve falhar."""
    with pytest.raises(ValidationError) as exc:
        _manager_teste().execute_plan(_plano(), context=_contexto(task_id="outra"))
    assert exc.value.code == "wsai.execution.task_mismatch"


# --- Gestor: execução bem-sucedida -----------------------------------------


def test_gestor_executa_plano_com_sucesso() -> None:
    """Os passos devem correr na ordem e todos concluir com sucesso."""
    chamadas: list[int] = []

    def runner(indice: int, passo: str) -> None:
        chamadas.append(indice)
        assert isinstance(passo, str) and passo

    relatorio: ExecutionReport = _manager_teste().execute_plan(
        _plano(),
        step_runner=runner,
    )

    assert relatorio.status is ExecutionStatus.SUCCESS
    assert relatorio.error is None
    assert relatorio.is_success is True
    assert relatorio.task_id == "task-1"
    assert relatorio.execution_id == "exec-task-1"
    assert chamadas == [0, 1, 2]
    assert len(relatorio.steps) == 3
    assert all(passo.passed for passo in relatorio.steps)
    assert all(passo.status is StepStatus.SUCCESS for passo in relatorio.steps)
    assert relatorio.duration >= 0.0
    assert "ok" in relatorio.summary


def test_gestor_usa_contexto_fornecido() -> None:
    """O contexto fornecido deve prevalecer (identidade e budget)."""
    relatorio = _manager_teste().execute_plan(
        _plano(),
        context=_contexto(execution_id="exec-especial"),
    )
    assert relatorio.execution_id == "exec-especial"


def test_gestor_sem_runner_executa_sem_operacao() -> None:
    """Sem runner, os passos são observados sem operação real."""
    relatorio = _manager_teste().execute_plan(_plano())
    assert relatorio.is_success is True
    assert len(relatorio.steps) == 3


def test_gestor_plano_sem_passos() -> None:
    """Um plano executável sem passos deve concluir sem observações."""
    relatorio = _manager_teste().execute_plan(_plano(steps=()))
    assert relatorio.is_success is True
    assert relatorio.steps == ()


# --- Gestor: falhas, tempo e cancelamento --------------------------------


def test_gestor_marca_falha_e_skipa_restantes() -> None:
    """A primeira falha deve marcar o passo e deixar os restantes 'SKIPPED'."""

    def runner(indice: int, passo: str) -> None:
        if indice == 1:
            raise ValueError("simulação de falha")

    relatorio = _manager_teste().execute_plan(_plano(), step_runner=runner)

    assert relatorio.status is ExecutionStatus.FAILED
    assert relatorio.is_success is False
    assert [p.status for p in relatorio.steps] == [
        StepStatus.SUCCESS,
        StepStatus.FAILED,
        StepStatus.SKIPPED,
    ]
    falhado = relatorio.steps[1]
    assert isinstance(falhado.error, ExecutionError)
    assert falhado.error.code == "wsai.execution.step_failed"


def test_gestor_preserva_erro_taxonomico_do_passo() -> None:
    """Um erro já taxonómico do passo deve ser preservado."""

    def runner(indice: int, passo: str) -> None:
        raise ProviderError("fornecedor indisponível")

    relatorio = _manager_teste().execute_plan(_plano(), step_runner=runner)

    assert relatorio.status is ExecutionStatus.FAILED
    assert isinstance(relatorio.error, ProviderError)


def test_gestor_cancelamento_antecipado() -> None:
    """Com o token cancelado antes de começar, a execução é cancelada."""
    token = CancellationToken()
    token.cancel()

    relatorio = _manager_teste().execute_plan(
        _plano(),
        context=_contexto(cancellation=token),
    )

    assert relatorio.status is ExecutionStatus.CANCELLED
    assert isinstance(relatorio.error, CancellationError)
    assert relatorio.steps == ()


def test_gestor_timeout_do_plano() -> None:
    """Exceder a duração da política deve marcar a execução como TIMEOUT."""

    def runner(indice: int, passo: str) -> None:
        time.sleep(5.0)

    relatorio = _manager_teste().execute_plan(
        _plano(),
        step_runner=runner,
        timeout=TimeoutPolicy(duration_seconds=0.01),
    )

    assert relatorio.status is ExecutionStatus.TIMEOUT
    assert isinstance(relatorio.error, WsaiError)
    assert relatorio.error.code == "wsai.timeout.exceeded"
    assert not relatorio.is_success


def test_gestor_recuperacao_repete_o_plano() -> None:
    """A recuperação deve repetir o plano inteiro até ao sucesso."""
    tentativas = [0]

    def runner(indice: int, passo: str) -> None:
        tentativas[0] += 1
        if tentativas[0] <= 2:
            raise ProviderError("falha transitória")

    relatorio = _manager_teste().execute_plan(
        _plano(),
        step_runner=runner,
        recovery=RecoveryPolicy(
            max_attempts=3,
            retry_error_types=(ProviderError,),
            base_delay_seconds=0.0,
        ),
    )

    assert relatorio.status is ExecutionStatus.SUCCESS
    assert tentativas[0] == 5
    assert len(relatorio.steps) == 3
    assert all(passo.passed for passo in relatorio.steps)


# --- Gestor: governação de recursos ---------------------------------------


def test_gestor_reserva_e_liberta_recursos() -> None:
    """O orçamento do contexto deve ser reservado e libertado no fim."""
    governador = _governador()
    visto_durante: list[int] = []

    def runner(indice: int, passo: str) -> None:
        visto_durante.append(len(governador.outstanding))

    relatorio = _manager_teste(governor=governador).execute_plan(
        _plano(),
        context=_contexto(
            budget=(ResourceLimit(name="ram", value=0.5),),
        ),
        step_runner=runner,
    )

    assert relatorio.is_success is True
    assert visto_durante == [1, 1, 1]
    assert governador.outstanding == ()


def test_gestor_falha_de_orcamento_marca_execucao() -> None:
    """Um orçamento insatisfeito deve falhar a execução sem passos."""
    relatorio = _manager_teste(governor=_governador()).execute_plan(
        _plano(),
        context=_contexto(
            budget=(ResourceLimit(name="ram", value=999.0),),
        ),
    )

    assert relatorio.status is ExecutionStatus.FAILED
    assert isinstance(relatorio.error, ResourceError)
    assert relatorio.steps == ()


# --- Gestor: integração com o Task Intelligence ----------------------------


def test_gestor_executa_plano_da_fase_7() -> None:
    """Um plano real do Task Intelligence deve executar integralmente."""
    plano = build_execution_plan(
        Task(id="t-chat", kind=TaskKind.CHAT, prompt="Olá"),
        create_capability_registry(),
        _hardware(),
        _runtime(available_gb=10.0),
        create_model_registry(),
        _fornecedor_saudavel(("local_llm_inference",)),
    )
    vistos: list[str] = []

    def runner(indice: int, passo: str) -> None:
        vistos.append(passo)

    relatorio = _manager_teste().execute_plan(plano, step_runner=runner)

    assert plano.is_executable is True
    assert relatorio.is_success is True
    assert vistos == list(plano.steps)
    assert plano.steps != ()
    assert "ok" in relatorio.summary


# --- Scheduler -------------------------------------------------------------


def _manager_teste(**kwargs: object) -> RuntimeManager:
    """Constrói um gestor de teste."""
    return RuntimeManager(**kwargs)  # type: ignore[arg-type]


def _scheduler_teste() -> Scheduler:
    """Constrói um scheduler de teste sobre um gestor real."""
    return Scheduler(_manager_teste())


def test_scheduler_ordena_por_prioridade() -> None:
    """A ordem de execução deve respeitar a prioridade (crítica primeiro)."""
    plano_critico = _plano(task_id="critica", steps=("a",))
    plano_baixo = _plano(task_id="baixa", steps=("a",))
    plano_normal = _plano(task_id="normal", steps=("a",))

    relatorio: SchedulerReport = _scheduler_teste().run(
        (plano_baixo, plano_normal, plano_critico),
        priorities={
            "critica": ExecutionPriority.CRITICAL,
            "normal": ExecutionPriority.NORMAL,
            "baixa": ExecutionPriority.LOW,
        },
    )

    assert relatorio.order == ("critica", "normal", "baixa")
    assert [o.priority for o in relatorio.outcomes] == [
        ExecutionPriority.CRITICAL,
        ExecutionPriority.NORMAL,
        ExecutionPriority.LOW,
    ]
    assert [o.task_id for o in relatorio.outcomes] == list(relatorio.order)


def test_scheduler_estavel_na_mesma_prioridade() -> None:
    """Sem prioridade definida, a ordem fornecida deve manter-se (estável)."""
    relatorio = _scheduler_teste().run(
        (_plano(task_id="p1", steps=("a",)), _plano(task_id="p2", steps=("a",))),
    )
    assert relatorio.order == ("p1", "p2")
    assert relatorio.succeeded == 2
    assert relatorio.failed == 0


def test_scheduler_aplica_factory_de_contexto() -> None:
    """O 'context_factory' deve construir o contexto de cada plano."""
    vistos: list[str] = []

    def factory(plano: ExecutionPlan) -> ExecutionContext:
        vistos.append(plano.task_id)
        return _contexto(
            execution_id=f"exec-{plano.task_id}",
            task_id=plano.task_id,
        )

    relatorio = _scheduler_teste().run(
        (_plano(task_id="p1", steps=("a",)), _plano(task_id="p2", steps=("a",))),
        context_factory=factory,
    )

    assert vistos == ["p1", "p2"]
    assert relatorio.outcomes[0].report.execution_id == "exec-p1"
    assert relatorio.outcomes[1].report.execution_id == "exec-p2"


def test_scheduler_report_contagens_com_falha() -> None:
    """Um plano falhado deve contar como falha no relatório agregado."""

    class _GestorFalso:
        """Gestor que falha determinísticamente para um plano específico."""

        def __init__(self) -> None:
            self.execucoes: list[str] = []

        def execute_plan(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext | None = None,
            *,
            step_runner: object | None = None,
            timeout: object | None = None,
            recovery: object | None = None,
        ) -> ExecutionReport:
            self.execucoes.append(plan.task_id)
            if plan.task_id == "falha":
                return ExecutionReport(
                    execution_id="exec-falha",
                    task_id="falha",
                    status=ExecutionStatus.FAILED,
                    steps=(),
                    duration=0.1,
                    error=ExecutionError("falhou", code="wsai.execution.step_failed"),
                )
            return ExecutionReport(
                execution_id=f"exec-{plan.task_id}",
                task_id=plan.task_id,
                status=ExecutionStatus.SUCCESS,
                steps=(),
                duration=0.01,
            )

    gestor = _GestorFalso()
    relatorio = Scheduler(gestor).run(
        (_plano(task_id="ok", steps=("a",)), _plano(task_id="falha", steps=("a",))),
    )

    assert relatorio.total == 2
    assert relatorio.succeeded == 1
    assert relatorio.failed == 1
    assert gestor.execucoes == ["ok", "falha"]


def test_scheduler_continua_apos_falha_por_omissao() -> None:
    """Por omissão, o scheduler deve continuar após uma falha de plano."""

    class _GestorFalhaPrimeiro:
        """Gestor que falha apenas no primeiro plano."""

        def __init__(self) -> None:
            self.execucoes: list[str] = []

        def execute_plan(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext | None = None,
            *,
            step_runner: object | None = None,
            timeout: object | None = None,
            recovery: object | None = None,
        ) -> ExecutionReport:
            self.execucoes.append(plan.task_id)
            falhou = plan.task_id == "primeiro"
            return ExecutionReport(
                execution_id=f"exec-{plan.task_id}",
                task_id=plan.task_id,
                status=ExecutionStatus.FAILED if falhou else ExecutionStatus.SUCCESS,
                steps=(),
                duration=0.01,
                error=ExecutionError("falhou") if falhou else None,
            )

    gestor = _GestorFalhaPrimeiro()
    relatorio = Scheduler(gestor).run(
        (
            _plano(task_id="primeiro", steps=("a",)),
            _plano(task_id="segundo", steps=("a",)),
        ),
    )

    assert relatorio.order == ("primeiro", "segundo")
    assert relatorio.failed == 1
    assert relatorio.succeeded == 1
    assert gestor.execucoes == ["primeiro", "segundo"]


def test_scheduler_para_em_falha() -> None:
    """Com 'stop_on_failure', o scheduler deve interromper na primeira falha."""

    class _GestorSempreFalha:
        """Gestor que falha sempre."""

        def __init__(self) -> None:
            self.execucoes: list[str] = []

        def execute_plan(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext | None = None,
            *,
            step_runner: object | None = None,
            timeout: object | None = None,
            recovery: object | None = None,
        ) -> ExecutionReport:
            self.execucoes.append(plan.task_id)
            return ExecutionReport(
                execution_id=f"exec-{plan.task_id}",
                task_id=plan.task_id,
                status=ExecutionStatus.FAILED,
                steps=(),
                duration=0.01,
                error=ExecutionError("falhou", code="wsai.execution.step_failed"),
            )

    gestor = _GestorSempreFalha()
    relatorio = Scheduler(gestor).run(
        (
            _plano(task_id="p1", steps=("a",)),
            _plano(task_id="p2", steps=("a",)),
            _plano(task_id="p3", steps=("a",)),
        ),
        stop_on_failure=True,
    )

    assert relatorio.order == ("p1",)
    assert relatorio.total == 1
    assert relatorio.failed == 1
    assert gestor.execucoes == ["p1"]


def test_scheduler_relatorio_tipos_e_desenho() -> None:
    """O relatório deve expor metas, ordem e duração parciais."""

    class _GestorOk:
        """Gestor que devolve sucesso com observação de duração."""

        def execute_plan(
            self,
            plan: ExecutionPlan,
            context: ExecutionContext | None = None,
            *,
            step_runner: object | None = None,
            timeout: object | None = None,
            recovery: object | None = None,
        ) -> ExecutionReport:
            return ExecutionReport(
                execution_id=f"exec-{plan.task_id}",
                task_id=plan.task_id,
                status=ExecutionStatus.SUCCESS,
                steps=(
                    StepOutcome(
                        index=0,
                        step=plan.steps[0],
                        status=StepStatus.SUCCESS,
                        duration=0.0,
                    ),
                ),
                duration=0.01,
            )

    relatorio: SchedulerReport = Scheduler(_GestorOk()).run(  # type: ignore[arg-type]
        (_plano(task_id="u1", steps=("único",)),)
    )

    assert isinstance(relatorio.outcomes[0], ScheduleOutcome)
    assert relatorio.duration >= 0.0
    assert relatorio.total == 1
    assert "scheduler" in relatorio.summary