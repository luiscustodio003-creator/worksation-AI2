"""Contexto de execução do WorkStation AI 2.

Transporta de forma consistente (hardening 04 do CORE_HARDENING_PLAN)
os dados de uma execução: execution_id, task_id, project_id, deadline,
token de cancelamento cooperativo, budget de recursos e prioridade.

O cancelamento é **cooperativo** e thread-agnostic: o token não gere
threads nem bloqueia; apenas regista o pedido e valida-o onde a execução
o pedir (`raise_if_cancelled`). A governação real de timeout,
cancelamento e recuperação pertence às unidades 8.3/8.4.

Para manter o núcleo folha em runtime, a referência a `ResourceLimit` da
extensão (8.1) é tipográfica (`TYPE_CHECKING`), evitando uma dependência
circular futura quando a extensão adoptar a taxonomia de erros do core.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from .errors import CancellationError, ValidationError

if TYPE_CHECKING:
    from wsai2.extension import ResourceLimit


class ExecutionPriority(Enum):
    """Prioridade de uma execução."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CancellationToken:
    """Token cooperativo de cancelamento de uma execução.

    Regista o pedido de cancelamento e permite à execução validá-lo nos
    pontos de cancelamento. Não gere threads nem bloqueia.
    """

    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        """Regista o pedido de cancelamento."""
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Indica se o cancelamento foi pedido."""
        return self._cancelled

    def raise_if_cancelled(self) -> None:
        """Lança ``CancellationError`` se o cancelamento foi pedido."""
        if self._cancelled:
            raise CancellationError("execução cancelada")


@dataclass(frozen=True)
class ExecutionContext:
    """Contexto imutável de uma execução.

    Reúne a identidade da execução (execution_id), a tarefa (task_id), o
    projecto (project_id), o limite temporal (deadline em time.monotonic),
    o token de cancelamento, o budget declarativo de recursos e a
    prioridade. O token de cancelamento é mutável por referência — o
    contexto apenas o transporta.
    """

    execution_id: str
    task_id: str
    project_id: str = ""
    deadline: float | None = None
    cancellation: CancellationToken | None = None
    budget: tuple[ResourceLimit, ...] = field(default_factory=tuple)
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida o contexto no momento da criação."""
        if not self.execution_id:
            raise ValidationError("a execução precisa de um execution_id não vazio")
        if not self.task_id:
            raise ValidationError("a execução precisa de um task_id não vazio")
        if self.deadline is not None and self.deadline <= time.monotonic():
            raise ValidationError("a deadline deve estar no futuro")

    @property
    def has_deadline(self) -> bool:
        """Indica se a execução tem limite temporal."""
        return self.deadline is not None

    @property
    def remaining_seconds(self) -> float | None:
        """Tempo restante até à deadline, ou ``None`` sem deadline."""
        if self.deadline is None:
            return None
        return max(0.0, self.deadline - time.monotonic())

    @property
    def is_expired(self) -> bool:
        """Indica se a deadline já foi ultrapassada."""
        if self.deadline is None:
            return False
        return self.deadline <= time.monotonic()

    def raise_if_cancelled(self) -> None:
        """Valida o cancelamento cooperativo no contexto."""
        if self.cancellation is not None:
            self.cancellation.raise_if_cancelled()

    @property
    def summary(self) -> str:
        """Resumo textual do contexto para apresentação."""
        return f"exec {self.execution_id} (task {self.task_id})"


__all__ = [
    "CancellationToken",
    "ExecutionContext",
    "ExecutionPriority",
]