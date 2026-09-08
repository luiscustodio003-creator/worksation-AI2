"""Taxonomia transversal de erros do WorkStation AI 2.

Modelo de erros unificado (hardening 03 do CORE_HARDENING_PLAN),
criado porque a auditoria da Fase 8.2 mostrou que as excepções actuais
(`AdapterError`, `ProviderProbeError`, `ValueError`) não cobrem o
contrato de execução: faltam categorias para Execution, Timeout,
Cancellation, Resource, Permission e ProjectIsolation.

Cada categoria é uma classe com um `code` estável e um `details` opaco.
O módulo é folha — depende apenas de stdlib. Os erros existentes das
Fases 1–7 não são alterados nesta unidade; o alinhamento posterior do
`AdapterError` sobre `ProviderError` é aditivo e documentado no BASE-26.
"""

from __future__ import annotations


class WsaiError(Exception):
    """Erro base do WorkStation AI 2.

    Transporta um código estável da categoria e um dicionário de
    detalhes opacos, preservando a mensagem humana da excepção.
    """

    _code = "wsai.error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code or self._code
        self.details = dict(details or {})

    @property
    def message(self) -> str:
        """Mensagem descritiva do erro."""
        return str(self)


class ValidationError(WsaiError):
    """Dados ou argumentos inválidos."""

    _code = "wsai.validation"


class CapabilityError(WsaiError):
    """Falha de capacidade do sistema."""

    _code = "wsai.capability"


class ModelError(WsaiError):
    """Falha relacionada com um modelo."""

    _code = "wsai.model"


class ProviderError(WsaiError):
    """Falha de fornecedor; base futura do alinhamento do AdapterError."""

    _code = "wsai.provider"


class ResourceError(WsaiError):
    """Falha de governação de recursos."""

    _code = "wsai.resource"


class TimeoutError(WsaiError):
    """Deadline de execução excedido."""

    _code = "wsai.timeout"


class CancellationError(WsaiError):
    """Execução cancelada."""

    _code = "wsai.cancellation"


class PermissionError(WsaiError):
    """Permissões insuficientes."""

    _code = "wsai.permission"


class ProjectIsolationError(WsaiError):
    """Acesso cruzado entre projectos sem autorização."""

    _code = "wsai.project_isolation"


class ExecutionError(WsaiError):
    """Falha genérica de execução."""

    _code = "wsai.execution"


__all__ = [
    "CapabilityError",
    "CancellationError",
    "ExecutionError",
    "ModelError",
    "PermissionError",
    "ProjectIsolationError",
    "ProviderError",
    "ResourceError",
    "TimeoutError",
    "ValidationError",
    "WsaiError",
]