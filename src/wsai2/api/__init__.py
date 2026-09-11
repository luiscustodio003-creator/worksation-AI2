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
"""

from .base import ApiGateway, health
from .capabilities import capabilities
from .contract import ApiRequest, ApiResponse
from .hardware import hardware
from .models import models
from .runtime import runtime
from .system import system
from .transport_stdlib import StdLibHttpGateway

API_CONTRACT_VERSION = "1.0"

__all__ = [
    "ApiGateway",
    "ApiRequest",
    "ApiResponse",
    "StdLibHttpGateway",
    "capabilities",
    "hardware",
    "health",
    "models",
    "runtime",
    "system",
]