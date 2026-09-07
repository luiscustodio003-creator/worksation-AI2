"""Detecção de fornecedores no ambiente real.

Módulo de domínio puro: a detecção decide se um fornecedor registado
está presente e acessível, mas **não** executa I/O de rede. O contacto
com o endpoint é feito através de um *probe* injectável
(`ProviderProbe`), mantendo a lógica de domínio separada do código de
I/O (constituição arquitectural, artigo 5).

A implementação de probes concretas (ex.: HTTP) vive em `probes.py`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .base import ProviderDefinition, ProviderType
from .registry import ProviderRegistry


@dataclass(frozen=True)
class ProviderProbeResult:
    """Resultado do contacto com o endpoint de um fornecedor."""

    reachable: bool
    latency_ms: float | None = None
    error: str | None = None


# Assinatura de um probe: recebe a base_url e devolve o resultado.
ProviderProbe = Callable[[str], ProviderProbeResult]


@dataclass(frozen=True)
class ProviderDetection:
    """Resultado da detecção de um fornecedor no ambiente real."""

    provider_id: str
    name: str
    type: ProviderType
    base_url: str
    reachable: bool
    latency_ms: float | None = None
    error: str | None = None
    capabilities_provided: tuple[str, ...] = field(default_factory=tuple)

    @property
    def summary(self) -> str:
        """Resumo textual da detecção para apresentação."""
        estado = "disponível" if self.reachable else "indisponível"
        return f"{self.name} ({self.base_url}) — {estado}"


def detect_provider(
    definition: ProviderDefinition,
    probe: ProviderProbe,
    base_url: str | None = None,
) -> ProviderDetection:
    """Detecta um fornecedor usando o probe fornecido.

    A ``base_url`` efectiva é a indicada ou a predefinida na definição.
    """
    effective_base_url = base_url or definition.default_base_url

    result = probe(effective_base_url)
    return ProviderDetection(
        provider_id=definition.id,
        name=definition.name,
        type=definition.type,
        base_url=effective_base_url,
        reachable=result.reachable,
        latency_ms=result.latency_ms,
        error=result.error,
        capabilities_provided=definition.capabilities_provided,
    )


def detect_providers(
    registry: ProviderRegistry,
    probe: ProviderProbe,
    base_urls: dict[str, str] | None = None,
) -> tuple[ProviderDetection, ...]:
    """Detecta todos os fornecedores do registo.

    ``base_urls`` permite sobrescrever a base_url por fornecedor
    (chave: id do fornecedor). A ordem do resultado segue o id do
    fornecedor, para ser determinística.
    """
    overrides = base_urls or {}
    detections = [
        detect_provider(
            definition,
            probe,
            base_url=overrides.get(definition.id),
        )
        for definition in registry.all()
    ]
    return tuple(sorted(detections, key=lambda detection: detection.provider_id))


def available_providers(
    detections: tuple[ProviderDetection, ...],
) -> tuple[ProviderDetection, ...]:
    """Filtra as detecções devolvendo apenas os fornecedores acessíveis."""
    return tuple(detection for detection in detections if detection.reachable)


__all__ = [
    "ProviderDetection",
    "ProviderProbe",
    "ProviderProbeResult",
    "available_providers",
    "detect_provider",
    "detect_providers",
]