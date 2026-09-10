"""Contratos puros do subsistema API (Fase 10, API-01).

Define as mensagens de entrada/saída do gateway, sem lógica de negócio e
sem dependências de transporte: apenas dataclasses imutáveis usadas pelo
contrato dos handlers e pelos adaptadores de HTTP (transporte stdlib).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ApiRequest:
    """Pedido normalizado recebido por um ``ApiGateway``.

    O transporte converte o pedido HTTP num ``ApiRequest``; os handlers
    não conhecem o mecanismo de transporte.
    """

    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""


@dataclass(frozen=True)
class ApiResponse:
    """Resposta normalizada devolvida por um ``ApiGateway``.

    ``payload`` é serializável em JSON (dict/list/str/número/bool). O
    transporte converte esta resposta no formato concreto (HTTP/JSON).
    """

    status: int
    payload: dict[str, object] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)