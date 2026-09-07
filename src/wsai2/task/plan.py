"""Plano de execução de uma tarefa.

Fecha o ciclo do Task Intelligence: integra os requisitos da tarefa
(categoria, capacidades), a viabilidade perante o Capability Engine, a
recomendação de modelo (Model Intelligence) e um fornecedor saudável
(Provider Layer) num **plano de execução** determinístico.

O fornecedor saudável é **injectado** (tuple de `ProviderHealth`), tal
como o I/O dos health checks — o plano decide; os health checks
executam o contacto.
"""

from __future__ import annotations

from dataclasses import dataclass

from wsai2.capability import CapabilityRegistry
from wsai2.hardware import HardwareProfile
from wsai2.model import ModelRecommendation, ModelRegistry, recommend_model
from wsai2.provider import ProviderHealth, ProviderHealthStatus
from wsai2.runtime import RuntimeProfile

from .base import Task
from .capability_selection import select_capabilities
from .requirements import requirements_for


@dataclass(frozen=True)
class ExecutionPlan:
    """Plano de execução de uma tarefa.

    Reúne a decisão completa do Task Intelligence: género de modelo,
    modelo escolhido (se compatível), fornecedor saudável escolhido (se
    existir), viabilidade e passos a executar.
    """

    task_id: str
    category: str
    feasible: bool
    model_id: str | None
    provider_id: str | None
    reasons: tuple[str, ...]
    steps: tuple[str, ...]

    @property
    def is_executable(self) -> bool:
        """Indica se o plano está pronto a executar."""
        return self.feasible and self.model_id is not None and self.provider_id is not None

    @property
    def summary(self) -> str:
        """Resumo textual do plano para apresentação."""
        if self.is_executable:
            return (
                f"{self.task_id}: executar com {self.model_id} "
                f"via {self.provider_id}"
            )
        return f"{self.task_id}: não executável ({len(self.reasons)} problemas)"


def _choose_provider(
    model_id: str,
    model_registry: ModelRegistry,
    provider_health: tuple[ProviderHealth, ...],
) -> ProviderHealth | None:
    """Escolhe o fornecedor saudável compatível com o modelo.

    Um fornecedor é candidato quando está saudável e disponibiliza
    capacidades que satisfazem as capacidades exigidas pelo modelo. A
    escolha é determinística (ordem por id do fornecedor).
    """
    model = model_registry.get(model_id)
    if model is None:
        return None
    required = set(model.requirements.required_capabilities)
    healthy = tuple(
        health
        for health in provider_health
        if health.status is ProviderHealthStatus.HEALTHY
        and not (required and not required.intersection(health.capabilities_provided))
    )
    if not healthy:
        return None
    return healthy[0]


def build_execution_plan(
    task: Task,
    capability_registry: CapabilityRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    model_registry: ModelRegistry,
    provider_health: tuple[ProviderHealth, ...] = (),
) -> ExecutionPlan:
    """Constrói o plano de execução de uma tarefa.

    Sequência: requisitos → viabilidade de capacidades → recomendação de
    modelo (por categoria) → escolha de fornecedor saudável → passos.
    """
    reasons: list[str] = []
    steps: list[str] = []

    requirements = requirements_for(task)
    category = requirements.category
    steps.append("verificar requisitos e capacidades da tarefa")

    selection = select_capabilities(
        requirements, capability_registry, hardware, runtime
    )
    if not selection.is_viable:
        reasons.append("faltam capacidades: " + ", ".join(selection.missing))
        steps.append("reportar inviabilidade por capacidades em falta")
        return _plan(task, category, False, None, None, reasons, steps)

    steps.append("recomendar modelo para a categoria adequada")
    recommendation: ModelRecommendation | None = recommend_model(
        model_registry, hardware, runtime, capability_registry, category=category
    )
    model_id: str | None = None
    if recommendation is None or not recommendation.is_suitable:
        reasons.append("nenhum modelo compatível recomendável")
    else:
        model_id = recommendation.model_id
        steps.append(f"usar modelo {model_id}")

    if model_id is None:
        return _plan(task, category, False, None, None, reasons, steps)

    steps.append("escolher fornecedor saudável compatível")
    provider = _choose_provider(model_id, model_registry, provider_health)
    provider_id: str | None = None
    if provider is None:
        reasons.append("nenhum fornecedor saudável compatível")
    else:
        provider_id = provider.provider_id
        steps.append(f"executar via {provider_id}")
        steps.append(f"gerar resposta (máx. {task.max_tokens} tokens)")

    return _plan(
        task,
        category,
        feasible=not reasons,
        model_id=model_id,
        provider_id=provider_id,
        reasons=reasons,
        steps=steps,
    )


def _plan(
    task: Task,
    category: object,
    feasible: bool,
    model_id: str | None,
    provider_id: str | None,
    reasons: list[str],
    steps: list[str],
) -> ExecutionPlan:
    """Constrói o plano final com os passos de execução."""
    return ExecutionPlan(
        task_id=task.id,
        category=category.value if hasattr(category, "value") else str(category),
        feasible=feasible,
        model_id=model_id,
        provider_id=provider_id,
        reasons=tuple(reasons),
        steps=tuple(steps),
    )


__all__ = ["ExecutionPlan", "build_execution_plan"]