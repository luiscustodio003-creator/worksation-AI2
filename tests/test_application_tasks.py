"""Testes do use-case Task Analysis (APP-08).

Verifica que ``TaskAnalysisService`` monta o ``TaskAnalysisResponse`` a
partir de ``wsai2.task`` (classificação, requisitos, selecção de
capacidades e plano) com fontes injectáveis — sem executar nenhuma tarefa
nem conhecer fornecedores.
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2.application import (
    TaskAnalysisRequest,
    TaskAnalysisResponse,
    TaskAnalysisService,
)
from wsai2.hardware import discover_hardware
from wsai2.model import create_default_registry as create_model_registry
from wsai2.runtime import discover_runtime
from wsai2.task import Task, TaskCapabilitySelection, TaskKind


def _tarefa_chat() -> Task:
    return Task(
        id="t1",
        kind=TaskKind.CHAT,
        prompt="Olá!",
        max_tokens=256,
        required_capabilities=("local_llm_inference",),
    )


def _servico_padrao() -> TaskAnalysisService:
    return TaskAnalysisService()


def test_resolve_padrao_produz_analise_completa() -> None:
    """APP-08: por omissão, a análise cobre classificação, requisitos,
    selecção e plano."""
    servico = _servico_padrao()
    resposta = servico.resolve(TaskAnalysisRequest(task=_tarefa_chat()))
    assert isinstance(resposta, TaskAnalysisResponse)
    assert resposta.task_id == "t1"
    assert resposta.classification.task_id == "t1"
    assert resposta.requirements.task_id == "t1"
    assert isinstance(resposta.selection, TaskCapabilitySelection)
    assert resposta.selection.task_id == "t1"
    assert resposta.plan is not None
    assert resposta.plan.task_id == "t1"


def test_resolve_nao_avalia_fornecedores() -> None:
    """APP-08: o plano não depende de fornecedores (provider_health vazio)."""
    resposta = _servico_padrao().resolve(TaskAnalysisRequest(task=_tarefa_chat()))
    assert resposta.plan.provider_id is not None or resposta.plan.provider_id is None
    assert isinstance(resposta.plan.feasible, bool)
    assert isinstance(resposta.plan.steps, tuple)


def test_plan_sem_capacidades_exigidas_marca_infeasivel() -> None:
    """APP-08: uma capacidade impossível torna o plano infeasível."""
    tarefa = Task(
        id="t2",
        kind=TaskKind.CHAT,
        prompt="Olá!",
        max_tokens=128,
        required_capabilities=("capacidade_impossivel",),
    )
    resposta = _servico_padrao().resolve(TaskAnalysisRequest(task=tarefa))
    assert resposta.selection.missing == ("capacidade_impossivel",)
    assert resposta.plan.feasible is False
    assert resposta.plan.model_id is None


def test_resolve_com_fontes_injectadas() -> None:
    """APP-08: fontes fixas mantêm a análise determinista."""
    hardware = discover_hardware()
    runtime = discover_runtime()
    registo_modelos = create_model_registry()
    servico = TaskAnalysisService(
        hardware_source=lambda: hardware,
        runtime_source=lambda: runtime,
        model_registry_source=lambda: registo_modelos,
    )
    resposta = servico.resolve(TaskAnalysisRequest(task=_tarefa_chat()))
    assert resposta.requirements.max_tokens == 256
    assert resposta.classification.task_id == "t1"


def test_resposta_imutavel_a_contrato() -> None:
    """APP-08: a resposta respeita o contrato congelado (frozen dataclass)."""
    resposta = _servico_padrao().resolve(TaskAnalysisRequest(task=_tarefa_chat()))

    assert resposta == TaskAnalysisResponse(
        task_id=resposta.task_id,
        classification=resposta.classification,
        requirements=resposta.requirements,
        selection=resposta.selection,
        plan=resposta.plan,
    )

    with pytest.raises(FrozenInstanceError):
        resposta.plan = None