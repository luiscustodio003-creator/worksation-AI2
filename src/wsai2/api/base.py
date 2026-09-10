"""Base dos handlers e contratos do subsistema API (API-01).

Define o interface ``ApiGateway`` (porte injectável que permite trocar o
transporte concreto sem alterar os handlers) e o serviço de exemplo
``health``, que expõe apenas versões do kernel/API — sem dependências de
domínio. A direcção das dependências é ``api -> core`` (unicamente através
de ``wsai2.core.public``, regra KERNEL-08).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from wsai2.core.public import CORE_PUBLIC_CONTRACT_VERSION

from .contract import ApiRequest, ApiResponse


class ApiGateway(ABC):
    """Porte do gateway HTTP da API.

    Um ``ApiGateway`` recebe um ``ApiRequest`` normalizado e devolve um
    ``ApiResponse`` normalizado. Cada adaptador de transporte (ex.:
    ``StdLibHttpGateway``) implementa o mapeamento para o protocolo
    concreto, mantendo os handlers independentes do transporte.
    """

    @abstractmethod
    def handle(self, request: ApiRequest) -> ApiResponse:
        """Processa um pedido e devolve uma resposta normalizada."""
        raise NotImplementedError


def health(request: ApiRequest) -> ApiResponse:
    """Endpoint de exemplo: expõe as versões de contrato do núcleo e da API.

    Não depende de nenhum domínio (hardware/runtime/capability/...); serve
    de ponto de integração do transporte e de sonda de estado da fundação.
    O método/rota são validados pelo transport/gateway; aqui assume-se
    ``GET /health`` já resolvido.
    """
    from wsai2.api import API_CONTRACT_VERSION  # no momento de chamada (evita ciclo)

    return ApiResponse(
        status=200,
        payload={
            "api": API_CONTRACT_VERSION,
            "core": CORE_PUBLIC_CONTRACT_VERSION,
            "status": "ok",
        },
    )