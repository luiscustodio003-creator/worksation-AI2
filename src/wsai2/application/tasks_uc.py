"""Serviço do use-case de análise de tarefa (APP-08).

Monta o ``TaskAnalysisResponse`` a partir de ``wsai2.task``
(classificação, requisitos, selecção de capacidades e plano de execução)
— a Application compõe os factos produzidos pelo domínio, sem tomar
decisões de execução nem conhecer fornecedores (``provider_health``
fica por omissão; aresta ``provider`` não pertence ao FIREWALL).
"""

from __future__ import annotations

from typing import Callable

from wsai2 import capability as _capability
from wsai2 import model as _model
from wsai2 import task as _task
from wsai2.hardware import HardwareProfile, discover_hardware
from wsai2.runtime import RuntimeProfile, discover_runtime

from .contract import TaskAnalysisRequest, TaskAnalysisResponse

CapabilityRegistrySource = Callable[[], _capability.CapabilityRegistry]
ModelRegistrySource = Callable[[], _model.ModelRegistry]
HardwareSource = Callable[[], HardwareProfile]
RuntimeSource = Callable[[], RuntimeProfile]


class TaskAnalysisService:
    """Resolve o use-case de análise de tarefa (APP-08).

    Attributes:
        capability_registry_source: fonte do registo de capacidades.
        hardware_source: fonte do perfil estrutural (Hardware Capability).
        runtime_source: fonte do estado momentâneo (Runtime State).
        model_registry_source: fonte do registo de definições de modelo.
    """

    def __init__(
        self,
        capability_registry_source: CapabilityRegistrySource | None = None,
        hardware_source: HardwareSource | None = None,
        runtime_source: RuntimeSource | None = None,
        model_registry_source: ModelRegistrySource | None = None,
    ) -> None:
        self._capability_registry_source = (
            capability_registry_source
            if capability_registry_source is not None
            else _capability.create_default_registry
        )
        self._hardware_source = (
            hardware_source if hardware_source is not None else discover_hardware
        )
        self._runtime_source = (
            runtime_source if runtime_source is not None else discover_runtime
        )
        self._model_registry_source = (
            model_registry_source
            if model_registry_source is not None
            else _model.create_default_registry
        )

    def resolve(self, request: TaskAnalysisRequest) -> TaskAnalysisResponse:
        """Devolve a análise completa da tarefa, sem executar nada."""
        tarefa = request.task
        classificacao = _task.classify_task(tarefa)
        requisitos = _task.requirements_for(tarefa)
        seleccao = _task.select_capabilities(
            requisitos,
            self._capability_registry_source(),
            self._hardware_source(),
            self._runtime_source(),
        )
        plano = _task.build_execution_plan(
            tarefa,
            self._capability_registry_source(),
            self._hardware_source(),
            self._runtime_source(),
            self._model_registry_source(),
        )
        return TaskAnalysisResponse(
            task_id=tarefa.id,
            classification=classificacao,
            requirements=requisitos,
            selection=seleccao,
            plan=plano,
        )