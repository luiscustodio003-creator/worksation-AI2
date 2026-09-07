"""Subsistema Provider Layer do WorkStation AI 2.

Responsável por isolar os fornecedores e motores concretos (runtimes
locais e APIs compatíveis) atrás de contratos estáveis (subsistema 3.6
da arquitectura).

Nesta unidade inicial são implementados os **contratos de fornecedor**
(`ProviderDefinition`) e o **registo central** com um catálogo base
declarativo. A detecção, os adaptadores de runtime e os health checks
fazem parte das unidades seguintes da Fase 6.
"""

from .base import ProviderDefinition, ProviderType
from .registry import ProviderRegistry, create_default_registry, default_providers

__all__ = [
    "ProviderDefinition",
    "ProviderRegistry",
    "ProviderType",
    "create_default_registry",
    "default_providers",
]