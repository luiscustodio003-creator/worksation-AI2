"""Subsistema Provider Layer do WorkStation AI 2.

Responsável por isolar os fornecedores e motores concretos (runtimes
locais e APIs compatíveis) atrás de contratos estáveis (subsistema 3.6
da arquitectura).

Nesta unidade são implementados os **adaptadores de runtime**: uma
interface estável de comunicação com os motores concretos (listar
modelos e gerar texto) por tipo de fornecedor, com o transporte HTTP
isolado em `transports.py` e injectável (padrão da detecção). A
detecção pertence à unidade anterior; os health checks à unidade
seguinte.
"""

from .adapters import (
    AdapterError,
    OllamaAdapter,
    OpenAiCompatibleAdapter,
    RuntimeAdapter,
    Transport,
    TransportResult,
    adapter_factory_names,
    build_adapter,
)
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
    "AdapterError",
    "OllamaAdapter",
    "OpenAiCompatibleAdapter",
    "ProviderDefinition",
    "ProviderDetection",
    "ProviderProbe",
    "ProviderProbeResult",
    "ProviderRegistry",
    "ProviderType",
    "RuntimeAdapter",
    "Transport",
    "TransportResult",
    "adapter_factory_names",
    "available_providers",
    "build_adapter",
    "create_default_registry",
    "default_providers",
    "detect_provider",
    "detect_providers",
]