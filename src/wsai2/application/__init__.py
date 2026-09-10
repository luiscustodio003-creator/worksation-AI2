"""Camada Application do WorkStation AI 2 — contratos de use-case (APP-02).

A Application define a fronteira estável dos use-cases do Ramo A e actua
como mecanismo de precipitação das decisões da fase Pós-Kernel: a API
consome contratos da aplicação e a aplicação consome as superfícies
públicas do núcleo e dos domínios (constituição, artigo 7; arquitectura,
secção 3.10).

Responsabilidade: tipar as mensagens de pedido/resposta por área de
use-case (system, hardware, runtime, capabilities, models, tasks,
knowledge e execution/status/cancellation) reutilizando os tipos de
domínio existentes — sem lógica central de negócio, sem I/O e sem estado
persistente.

Dependências (fronteiras): capability, core, hardware, knowledge, model,
platform, runtime, runtime_engine e task — todas consumidas ao nível do
pacote.
"""

from .capabilities_uc import CapabilitiesService
from .contract import (
    CancellationRequest,
    CancellationResponse,
    CapabilitiesRequest,
    CapabilitiesResponse,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatusRequest,
    ExecutionStatusResponse,
    HardwareProfileRequest,
    HardwareProfileResponse,
    KnowledgeContextRequest,
    KnowledgeContextResponse,
    ModelsRequest,
    ModelsResponse,
    RuntimeProfileRequest,
    RuntimeProfileResponse,
    SystemInfoRequest,
    SystemInfoResponse,
    TaskAnalysisRequest,
    TaskAnalysisResponse,
)
from .hardware_uc import HardwareProfileService
from .models_uc import ModelsService
from .runtime_uc import RuntimeProfileService
from .system import SystemInfoService
from .tasks_uc import TaskAnalysisService

APPLICATION_CONTRACT_VERSION = "1.0"

__all__ = [
    "CancellationRequest",
    "CancellationResponse",
    "CapabilitiesRequest",
    "CapabilitiesResponse",
    "CapabilitiesService",
    "ExecutionRequest",
    "ExecutionResponse",
    "ExecutionStatusRequest",
    "ExecutionStatusResponse",
    "HardwareProfileRequest",
    "HardwareProfileResponse",
    "HardwareProfileService",
    "KnowledgeContextRequest",
    "KnowledgeContextResponse",
    "ModelsRequest",
    "ModelsResponse",
    "ModelsService",
    "RuntimeProfileRequest",
    "RuntimeProfileResponse",
    "RuntimeProfileService",
    "SystemInfoRequest",
    "SystemInfoResponse",
    "SystemInfoService",
    "TaskAnalysisRequest",
    "TaskAnalysisResponse",
    "TaskAnalysisService",
]