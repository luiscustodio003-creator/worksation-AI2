"""Subsistema API do WorkStation AI 2 (Fase 10, API-01).

Camada Application que expõe capacidades reais do sistema através de
contratos estáveis (arquitectura 3.10). A fundação (API-01) define o
contrato de mensagens (``ApiRequest``/``ApiResponse``), o porte
``ApiGateway`` (transporte injectável — permite trocar ``http.server``
por outro transporte sem tocar nos handlers) e o serviço de exemplo
``health``, dependente apenas de ``wsai2.core.public`` (regra KERNEL-08).
"""

from .base import ApiGateway, health
from .contract import ApiRequest, ApiResponse
from .transport_stdlib import StdLibHttpGateway

API_CONTRACT_VERSION = "1.0"

__all__ = [
    "ApiGateway",
    "ApiRequest",
    "ApiResponse",
    "StdLibHttpGateway",
    "health",
]