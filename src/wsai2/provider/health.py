"""Health checks dos fornecedores.

Avalia a **saúde fina** de cada fornecedor, combinando a detecção
(presença/acessibilidade do endpoint) com os adaptadores (o motor
responde e sabe listar modelos). Tal como a detecção, o módulo é puro:
o I/O é injectado através de um *probe* e de um *adaptador*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .adapters import AdapterError, RuntimeAdapter
from .base import ProviderDefinition
from .detection import ProviderDetection
from .registry import ProviderRegistry


class ProviderHealthStatus(Enum):
    """Estado de saúde fina de um fornecedor."""

    HEALTHY = "healthy"        # acessível e o motor responde correctamente
    DEGRADED = "degraded"      # acessível, mas o motor não responde bem
    UNAVAILABLE = "unavailable"  # endpoint inacessível


@dataclass(frozen=True)
class ProviderHealth:
    """Resultado do health check de um fornecedor."""

    provider_id: str
    name: str
    base_url: str
    status: ProviderHealthStatus
    model_count: int | None = None
    latency_ms: float | None = None
    error: str | None = None
    capabilities_provided: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_healthy(self) -> bool:
        """Indica se o fornecedor está saudável."""
        return self.status is ProviderHealthStatus.HEALTHY

    @property
    def summary(self) -> str:
        """Resumo textual do health check."""
        return f"{self.name} ({self.base_url}) — {self.status.value}"


def check_provider_health(
    definition: ProviderDefinition,
    probe,
    adapter: RuntimeAdapter,
    base_url: str | None = None,
) -> ProviderHealth:
    """Verifica a saúde fina de um fornecedor.

    Combina a detecção (probe) com a interacção com o motor (adaptador):
    - endpoint inacessível → ``UNAVAILABLE``;
    - endpoint acessível mas o motor falha (AdapterError) → ``DEGRADED``;
    - motor responde → ``HEALTHY``, com o número de modelos.

    O ``probe`` é um callable ``(base_url) -> ProviderProbeResult``; o
    adaptador deve usar um transporte com o mesmo comportamento de I/O.
    """
    effective_base_url = base_url or definition.default_base_url

    detection: ProviderDetection = probe(effective_base_url)
    if not detection.reachable:
        return ProviderHealth(
            provider_id=definition.id,
            name=definition.name,
            base_url=effective_base_url,
            status=ProviderHealthStatus.UNAVAILABLE,
            latency_ms=detection.latency_ms,
            error=detection.error,
            capabilities_provided=definition.capabilities_provided,
        )

    try:
        models = adapter.list_models(effective_base_url)
    except AdapterError as exc:
        return ProviderHealth(
            provider_id=definition.id,
            name=definition.name,
            base_url=effective_base_url,
            status=ProviderHealthStatus.DEGRADED,
            latency_ms=detection.latency_ms,
            error=str(exc),
            capabilities_provided=definition.capabilities_provided,
        )

    return ProviderHealth(
        provider_id=definition.id,
        name=definition.name,
        base_url=effective_base_url,
        status=ProviderHealthStatus.HEALTHY,
        model_count=len(models),
        latency_ms=detection.latency_ms,
        capabilities_provided=definition.capabilities_provided,
    )


def check_providers_health(
    registry: ProviderRegistry,
    probe,
    transport,
    base_urls: dict[str, str] | None = None,
) -> tuple[ProviderHealth, ...]:
    """Verifica a saúde de todos os fornecedores do registo.

    Constrói o adaptador de cada fornecedor com ``build_adapter`` usando
    o ``transport`` injectado. ``base_urls`` sobrescreve a base_url por
    fornecedor. O resultado é ordenado por id, para ser determinístico.
    """
    from .adapters import build_adapter

    overrides = base_urls or {}
    results: list[ProviderHealth] = []
    for definition in registry.all():
        try:
            adapter = build_adapter(definition, transport)
        except AdapterError as exc:
            results.append(
                ProviderHealth(
                    provider_id=definition.id,
                    name=definition.name,
                    base_url=overrides.get(definition.id, definition.default_base_url),
                    status=ProviderHealthStatus.DEGRADED,
                    error=str(exc),
                    capabilities_provided=definition.capabilities_provided,
                )
            )
            continue
        results.append(
            check_provider_health(
                definition,
                probe,
                adapter,
                base_url=overrides.get(definition.id),
            )
        )
    return tuple(sorted(results, key=lambda health: health.provider_id))


def healthy_providers(
    results: tuple[ProviderHealth, ...],
) -> tuple[ProviderHealth, ...]:
    """Filtra os health checks devolvendo apenas os fornecedores saudáveis."""
    return tuple(result for result in results if result.is_healthy)


__all__ = [
    "ProviderHealth",
    "ProviderHealthStatus",
    "check_provider_health",
    "check_providers_health",
    "healthy_providers",
]