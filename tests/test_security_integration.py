"""Testes de integração de política e isolamento no Runtime Engine (8.8).

Valida o enforcement registado: a decisão de política é aplicada no
``RuntimeManager.execute_plan`` **antes do passo 1**; uma negação devolve
um ``ExecutionReport`` ``FAILED`` com ``PermissionError`` (taxonomia 8.2)
e os passos ``SKIPPED``; sem motor de política o comportamento é
preservado.
"""

import pytest

from wsai2.core import CancellationToken, ExecutionContext, ExecutionPriority
from wsai2.core.errors import PermissionError, ValidationError
from wsai2.runtime_engine import ExecutionStatus, RuntimeManager, StepStatus
from wsai2.security import PolicyEngine
from wsai2.task import ExecutionPlan


def _plano(
    task_id: str = "task-1",
    steps: tuple[str, ...] = ("preparar", "executar", "finalizar"),
) -> ExecutionPlan:
    """Constrói um plano de teste executável."""
    return ExecutionPlan(
        task_id=task_id,
        category="chat",
        feasible=True,
        model_id="llama-teste",
        provider_id="ollama",
        reasons=(),
        steps=steps,
    )


def _contexto(
    *,
    principal: str = "alice",
    project_id: str = "proj-1",
    task_id: str = "task-1",
) -> ExecutionContext:
    """Constrói um contexto com principal e projecto preenchidos."""
    return ExecutionContext(
        execution_id="exec-1",
        task_id=task_id,
        principal=principal,
        project_id=project_id,
        priority=ExecutionPriority.NORMAL,
        cancellation=CancellationToken(),
    )


def test_plano_autorizado_executa_normalmente() -> None:
    """Com política e acção concedida, o plano deve executar com sucesso."""
    motor = PolicyEngine({"alice": ("execute",)})
    gestor = RuntimeManager()
    relatorio = gestor.execute_plan(
        _plano(),
        _contexto(),
        policy=motor,
    )
    assert relatorio.status is ExecutionStatus.SUCCESS
    assert relatorio.error is None
    assert [passo.status for passo in relatorio.steps] == [
        StepStatus.SUCCESS,
        StepStatus.SUCCESS,
        StepStatus.SUCCESS,
    ]


def test_plano_nao_autorizado_falha_antes_do_passo_1() -> None:
    """A negação deve falhar o plano inteiro sem executar nenhum passo."""
    motor = PolicyEngine({"alice": ("code.run",)})
    executado: list[str] = []

    def runner(indice: int, passo: str) -> None:
        executado.append(passo)

    relatorio = RuntimeManager().execute_plan(
        _plano(),
        _contexto(),
        step_runner=runner,
        policy=motor,
    )
    assert relatorio.status is ExecutionStatus.FAILED
    assert isinstance(relatorio.error, PermissionError)
    assert relatorio.error.code == "wsai.permission"
    assert executado == []  # nenhum runner foi chamado
    assert [passo.status for passo in relatorio.steps] == [
        StepStatus.SKIPPED,
        StepStatus.SKIPPED,
        StepStatus.SKIPPED,
    ]
    assert relatorio.error.details["action"] == "execute"
    assert relatorio.error.details["principal"] == "alice"


def test_principal_falta_levanta_validation_error() -> None:
    """Com política, um contexto sem principal é rejeitado à entrada."""
    contexto = _contexto(principal="")
    with pytest.raises(ValidationError) as erro:
        RuntimeManager().execute_plan(_plano(), contexto, policy=PolicyEngine())
    assert erro.value.code == "wsai.security.principal"


def test_projecto_falta_levanta_validation_error() -> None:
    """Com política, um contexto sem projecto é rejeitado à entrada."""
    contexto = _contexto(project_id="")
    with pytest.raises(ValidationError) as erro:
        RuntimeManager().execute_plan(_plano(), contexto, policy=PolicyEngine({"alice": ("execute",)}))
    assert erro.value.code == "wsai.security.project"


def test_contexto_omisso_sem_policy_mantem_comportamento() -> None:
    """Sem política, o contexto por omissão continua a funcionar (regressão)."""
    relatorio = RuntimeManager().execute_plan(_plano())
    assert relatorio.status is ExecutionStatus.SUCCESS
    assert relatorio.execution_id == "exec-task-1"


def test_error_isolation_no_relatorio() -> None:
    """A guarda de isolamento deve produzir o erro taxonómico 8.2."""
    from wsai2.security import assert_same_project

    from wsai2.core.errors import ProjectIsolationError

    gestor = RuntimeManager()
    motor = PolicyEngine({"alice": ("execute",)})
    relatorio = gestor.execute_plan(_plano(), _contexto(), policy=motor)
    assert relatorio.status is ExecutionStatus.SUCCESS
    with pytest.raises(ProjectIsolationError) as erro:
        assert_same_project("proj-1", "proj-2")
    assert erro.value.code == "wsai.project_isolation"