"""Critério executável do Gate — Core pronto para addons (Fase 8.9).

O Gate de addons (CORE_HARDENING_PLAN) não é um novo módulo: é a
formalização da base. Esta suíte funciona como **fotografia executável**
dos pré-requisitos públicos (contratos, lifecycle, recursos, timeout/
cancelamento/recuperação, compatibilidade, segurança, isolamento e
contrato arquitectural) e verifica as duas integrações registadas na 8.9:

- a **propagação da política** do ``Scheduler`` para o ``RuntimeManager``
  (contrato de composição: quem cria o runtime passa o motor);
- a **ponte permissions→grants** no ``ExtensionRegistry`` (as permissões
declaradas tornam-se acções exactas do principal = id da extensão).

Se algum destes testes falhar, a base deixou de satisfazer o critério do
Gate — voltar à auditoria antes de declarar addons prontos.
"""

from __future__ import annotations

import pytest

from wsai2.core import CancellationToken, ExecutionContext, ExecutionPriority
from wsai2.core.errors import PermissionError, ProjectIsolationError
from wsai2.extension import (
    ExtensionContract,
    ExtensionKind,
    ExtensionLifecycleState,
    ExtensionRegistry,
    transition,
)
from wsai2.runtime_engine import (
    ExecutionStatus,
    RuntimeManager,
    Scheduler,
    StepStatus,
)
from wsai2.security import PolicyEngine, assert_same_project, require_project
from wsai2.task import ExecutionPlan


def _contrato_extensao(
    *,
    identidade: str = "wsai.code",
    permissions: tuple[str, ...] = ("execute", "code.run"),
) -> ExtensionContract:
    """Constrói um contrato de extensão de grande impacto no estado VALIDATED."""
    return ExtensionContract(
        id=identidade,
        name="Extensão de Código",
        description="Extensão que executa código (Gate de addons).",
        kind=ExtensionKind.CODE,
        version="1.0.0",
        contract_version="1.0",
        lifecycle=ExtensionLifecycleState.VALIDATED,
        permissions=permissions,
    )


def _plano(task_id: str = "task-1") -> ExecutionPlan:
    """Constrói um plano de teste executável."""
    return ExecutionPlan(
        task_id=task_id,
        category="chat",
        feasible=True,
        model_id="llama-teste",
        provider_id="ollama",
        reasons=(),
        steps=("preparar", "executar", "finalizar"),
    )


def _contexto(task_id: str = "task-1", *, principal: str) -> ExecutionContext:
    """Constrói um contexto de execução com principal e projecto."""
    return ExecutionContext(
        execution_id=f"exec-{task_id}",
        task_id=task_id,
        principal=principal,
        project_id="proj-1",
        priority=ExecutionPriority.NORMAL,
        cancellation=CancellationToken(),
    )


def test_pre_requisitos_publicos_do_gate_existem() -> None:
    """O Gate exige que os pré-requisitos estejam alcançáveis na API pública."""
    from dataclasses import fields

    assert any(campo.name == "permissions" for campo in fields(ExtensionContract))
    assert any(campo.name == "resources" for campo in fields(ExtensionContract))
    assert hasattr(ExtensionLifecycleState, "READY")
    assert hasattr(ExtensionRegistry, "register")
    assert callable(transition)

    from wsai2.core.context import ExecutionContext
    from wsai2.execution import DeadlineGuard, run_with_timeout

    assert hasattr(ExecutionContext, "cancellation")
    assert hasattr(ExecutionContext, "project_id")
    assert callable(DeadlineGuard)
    assert callable(run_with_timeout)


def test_politica_propagada_agendamento_autorizado() -> None:
    """Com política e acção concedida, o agendamento deve executar tudo."""
    motor = PolicyEngine({"alice": ("execute",)})
    relatorio = Scheduler(RuntimeManager()).run(
        (_plano(),),
        context_factory=lambda plano: _contexto(principal="alice"),
        policy=motor,
    )
    assert relatorio.order == ("task-1",)
    assert relatorio.succeeded == 1
    assert relatorio.outcomes[0].report.status is ExecutionStatus.SUCCESS
    assert [p.status for p in relatorio.outcomes[0].report.steps] == [
        StepStatus.SUCCESS,
        StepStatus.SUCCESS,
        StepStatus.SUCCESS,
    ]


def test_politica_propagada_negacao_antes_do_passo_1() -> None:
    """A negação deve chegar ao gestor e falhar sem executar nenhum passo."""
    motor = PolicyEngine({"alice": ("code.run",)})
    executado: list[str] = []

    def runner(indice: int, passo: str) -> None:
        executado.append(passo)

    gestor = RuntimeManager()
    relatorio = Scheduler(gestor).run(
        (_plano(),),
        context_factory=lambda plano: _contexto(principal="alice"),
        policy=motor,
        step_runner=runner,
    )
    assert relatorio.failed == 1
    erro = relatorio.outcomes[0].report.error
    assert isinstance(erro, PermissionError)
    assert erro.code == "wsai.permission"
    assert executado == []
    assert [p.status for p in relatorio.outcomes[0].report.steps] == [
        StepStatus.SKIPPED,
        StepStatus.SKIPPED,
        StepStatus.SKIPPED,
    ]


def test_agendamento_sem_policy_preserva_comportamento() -> None:
    """Sem motor, o agendamento deve comportar-se exactamente como antes."""
    relatorio = Scheduler(RuntimeManager()).run((_plano(),))
    assert relatorio.succeeded == 1
    assert relatorio.outcomes[0].report.status is ExecutionStatus.SUCCESS


def test_registo_alimenta_politica_por_identidade_de_extensao() -> None:
    """Permissions declaradas tornam-se acções exactas da extensão (ponte)."""
    motor = PolicyEngine()
    ExtensionRegistry().register(_contrato_extensao(), policy=motor)
    assert motor.decide("wsai.code", "proj-1", "execute").allowed is True
    assert motor.decide("wsai.code", "proj-1", "code.run").allowed is True
    assert motor.decide("wsai.code", "proj-1", "github_push").allowed is False
    assert motor.decide("outra.extensao", "proj-1", "execute").allowed is False


def test_politica_vazia_nega_addon_sem_grants() -> None:
    """Sem grants (exact-match), a política vazia nega por omissão."""
    motor = PolicyEngine()
    ExtensionRegistry().register(_contrato_extensao(permissions=()), policy=motor)
    assert motor.decide("wsai.code", "proj-1", "execute").allowed is False


def test_isolamento_de_projectos_activo_e_taxonomico() -> None:
    """A fronteira de projectos (hardening 10) deve estar activa no Gate."""
    assert require_project("proj-1") == "proj-1"
    with pytest.raises(ProjectIsolationError) as erro:
        assert_same_project("proj-1", "proj-2")
    assert erro.value.code == "wsai.project_isolation"
