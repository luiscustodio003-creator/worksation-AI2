"""Núcleo transversal do WorkStation AI 2.

Camada folha do núcleo (constituição, artigo 2): contém a taxonomia
transversal de erros (hardening 03) e o contexto de execução com
cancelamento cooperativo (hardening 04), consumíveis por qualquer
subsistema sem criar dependências circulares.
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

__all__ = [
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