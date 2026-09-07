"""Subsistema Provider Layer do WorkStation AI 2.

Responsável por isolar os fornecedores e motores concretos (runtimes
locais e APIs compatíveis) atrás de contratos estáveis (subsistema 3.6
da arquitectura).

Nesta unidade é implementada a **detecção de fornecedores** no ambiente
real: a presença e a acessibilidade são verificadas por um probe
injectável, mantendo o I/O de rede (`probes.py`) isolado da lógica de
domínio (`detection.py`). Os contratos (`ProviderDefinition`) e o
registo (`ProviderRegistry`) provêm da unidade inicial da Fase 6; os
adaptadores de runtime e os health checks pertencem às unidades
seguintes.
"""

from .base import ProviderDefinition, ProviderType
from .detection import (
    ProviderDetection,
    ProviderProbe,
    ProviderProbeResult,
    available_providers,
    detect_provider,
    detect_providers,
)
from .registry import ProviderRegistry, create_default_registry, default_providers

__all__ = [
    "ProviderDefinition",
    "ProviderDetection",
    "ProviderProbe",
    "ProviderProbeResult",
    "ProviderRegistry",
    "ProviderType",
    "available_providers",
    "create_default_registry",
    "default_providers",
    "detect_provider",
    "detect_providers",
]