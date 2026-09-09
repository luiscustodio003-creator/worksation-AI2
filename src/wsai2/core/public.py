"""Superfície pública do núcleo (KERNEL-03).

Contrato versionado que expõe aos consumidores externos (futuros API/UI/
addons) os contratos estáveis do `core` folha: a taxonomia transversal de
erros e o contexto de execução com cancelamento cooperativo.

Esta fachada não introduz lógica nova nem altera fronteiras: depende
apenas de `wsai2.core.errors` e `wsai2.core.context` — `core` permanece
camada folha (constituição, artigo 2). As superfícies públicas de
execution, resource, runtime_engine e security são definidas por unidade
de fronteira (KERNEL-05/06), fora do leaf.
"""

from .context import CancellationToken, ExecutionContext, ExecutionPriority
from .errors import (
    CapabilityError,
    CancellationError,
    ExecutionError,
    ModelError,
    PermissionError,
    ProjectIsolationError,
    ProviderError,
    ResourceError,
    TimeoutError,
    ValidationError,
    WsaiError,
)

CORE_PUBLIC_CONTRACT_VERSION = "1.0"

__all__ = [
    "CORE_PUBLIC_CONTRACT_VERSION",
    "CancellationToken",
    "CapabilityError",
    "CancellationError",
    "ExecutionContext",
    "ExecutionError",
    "ExecutionPriority",
    "ModelError",
    "PermissionError",
    "ProjectIsolationError",
    "ProviderError",
    "ResourceError",
    "TimeoutError",
    "ValidationError",
    "WsaiError",
]