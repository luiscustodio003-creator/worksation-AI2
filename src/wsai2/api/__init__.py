"""Subsistema API do WorkStation AI 2 (Fase 10, API-01).

Camada Application que expõe capacidades reais do sistema através de
contratos estáveis (arquitectura 3.10). A fundação (API-01) define o
contrato de mensagens (``ApiRequest``/``ApiResponse``), o porte
``ApiGateway`` (transporte injectável — permite trocar ``http.server``
por outro transporte sem tocar nos handlers) e o serviço de exemplo
``health``, dependente apenas de ``wsai2.core.public`` (regra KERNEL-08).
A unidade API-02 acrescenta o endpoint ``system``, que consome o
``SystemInfoService`` da camada Application (fronteira ``api -> application``).
A unidade API-03 acrescenta o endpoint ``hardware``, que apresenta o
``HardwareProfileService`` (perfil estrutural) com o mesmo padrão.
A unidade API-04 acrescenta o endpoint ``runtime``, que apresenta o
``RuntimeProfileService`` (estado momentâneo) com o mesmo padrão.
A unidade API-05 acrescenta o endpoint ``capabilities``, que apresenta o
``CapabilitiesService`` (catálogo de capacidades) com o mesmo padrão.
A unidade API-06 acrescenta o endpoint ``models``, que apresenta o
``ModelsService`` (veredictos de compatibilidade de modelos) com o mesmo
padrão.
A unidade API-07 acrescenta o endpoint ``tasks``, que apresenta o
``TaskAnalysisService`` (análise de tarefa) — primeiro endpoint POST,
aceita corpo JSON com a descrição da tarefa e devolve a análise completa.
A unidade API-08 acrescenta o endpoint ``knowledge``, que apresenta o
``KnowledgeContextService`` (contexto de conhecimento) — mesmo padrão
POST/corpo JSON, devolvendo correspondências e pacote de contexto.
A unidade API-09 acrescenta os endpoints ``execution_start``,
``execution_status`` e ``execution_cancel``, que apresentam os use-cases
``ExecutionService``, ``ExecutionStatusService`` e ``CancellationService``
(execução, estado e cancelamento) — três rotas que compõem o ciclo de vida
de uma execução.
"""

from .base import ApiGateway, health
from .capabilities import capabilities
from .contract import ApiRequest, ApiResponse
from .executions import execution_cancel, execution_start, execution_status
from .hardware import hardware
from .knowledge import knowledge
from .models import models
from .runtime import runtime
from .system import system
from .tasks import tasks
from .transport_stdlib import StdLibHttpGateway

API_CONTRACT_VERSION = "1.0"

__all__ = [
    "ApiGateway",
    "ApiRequest",
    "ApiResponse",
    "StdLibHttpGateway",
    "capabilities",
    "execution_cancel",
    "execution_start",
    "execution_status",
    "hardware",
    "health",
    "knowledge",
    "models",
    "runtime",
    "system",
    "tasks",
]