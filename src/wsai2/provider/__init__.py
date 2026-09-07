"""Subsistema Provider Layer do WorkStation AI 2.

Responsável por isolar os fornecedores e motores concretos (runtimes
locais e APIs compatíveis) atrás de contratos estáveis (subsistema 3.6
da arquitectura).

Nesta unidade são implementados os **health checks**: a saúde fina de
cada fornecedor (motor responde, número de modelos) combinando a
detecção e os adaptadores, com I/O sempre injectado. O fecho da Fase 6
compreende contratos, registo, detecção, adaptadores e health checks.
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
from .health import (
    ProviderHealth,
    ProviderHealthStatus,
    check_provider_health,
    check_providers_health,
    healthy_providers,
)
from .registry import ProviderRegistry, create_default_registry, default_providers

__all__ = [
    "AdapterError",
    "OllamaAdapter",
    "OpenAiCompatibleAdapter",
    "ProviderDefinition",
    "ProviderDetection",
    "ProviderHealth",
    "ProviderHealthStatus",
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
    "check_provider_health",
    "check_providers_health",
    "create_default_registry",
    "default_providers",
    "detect_provider",
    "detect_providers",
    "healthy_providers",
]