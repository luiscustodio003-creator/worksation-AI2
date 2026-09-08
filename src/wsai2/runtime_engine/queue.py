"""Filas multicamadas do Runtime Engine.

A fila é uma camada aditiva sobre o ``Scheduler``: mantém uma fila pronta
ordenada por prioridade, um backlog de espera e preempção **de itens ainda
não iniciados**. Não interrompe trabalho em execução.

A capacidade da fila pronta é opcional. Sem limite, a estrutura comporta-se
como uma priority queue. Com limite, a chegada de uma prioridade superior
pode deslocar o item pronto de menor prioridade para o backlog.
"""

from __future__ import annotations

import heapq
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, Sequence, TypeVar

from wsai2.core.context import ExecutionPriority
from wsai2.core.errors import ValidationError

if TYPE_CHECKING:
    from wsai2.task import ExecutionPlan

T = TypeVar("T")

_PRIORIDADE_ORDEM: dict[ExecutionPriority, int] = {
    ExecutionPriority.CRITICAL: 0,
    ExecutionPriority.HIGH: 1,
    ExecutionPriority.NORMAL: 2,
    ExecutionPriority.LOW: 3,
}


@dataclass(frozen=True)
class QueueItem(Generic[T]):
    """Item materializado na fila, com prioridade e ordem estável."""

    item: T
    priority: ExecutionPriority
    sequence: int


@dataclass(frozen=True)
class QueueSnapshot:
    """Fotografia imutável da fila para observabilidade e testes."""

    ready: int
    backlog: int
    total: int


class MultilayerExecutionQueue(Generic[T]):
    """Fila pronta + backlog com prioridade determinística.

    A preempção ocorre somente sobre trabalho **pendente**: uma entrada
    superior pode retirar do conjunto pronto a entrada de menor prioridade,
    enviando-a para o backlog. Nenhum item já devolvido por ``pop_next`` é
    interrompido ou revertido.
    """

    def __init__(
        self,
        *,
        max_ready: int | None = None,
    ) -> None:
        if max_ready is not None and (
            not isinstance(max_ready, int)
            or isinstance(max_ready, bool)
            or max_ready < 1
        ):
            raise ValidationError(
                "max_ready tem de ser um inteiro >= 1 ou None",
                code="wsai.runtime.queue.capacity",
            )
        self._max_ready = max_ready
        self._ready: list[tuple[int, int, T]] = []
        self._backlog: list[tuple[int, int, T]] = []
        self._sequence = 0
        self._lock = threading.RLock()

    @property
    def max_ready(self) -> int | None:
        """Capacidade máxima da camada pronta, quando definida."""
        return self._max_ready

    def enqueue(self, item: T, priority: ExecutionPriority) -> None:
        """Adiciona um item à fila e aplica preempção de pendentes se necessário."""
        with self._lock:
            sequence = self._sequence
            self._sequence += 1
            rank = _PRIORIDADE_ORDEM[priority]

            if self._max_ready is None or len(self._ready) < self._max_ready:
                heapq.heappush(self._ready, (rank, sequence, item))
                return

            # O maior rank é a menor prioridade. Em empate, o mais recente
            # perde primeiro, preservando os itens antigos de igual prioridade.
            worst_index = max(
                range(len(self._ready)),
                key=lambda index: (self._ready[index][0], -self._ready[index][1]),
            )
            worst = self._ready[worst_index]
            if (rank, sequence) < (worst[0], worst[1]):
                self._ready[worst_index] = (rank, sequence, item)
                heapq.heapify(self._ready)
                heapq.heappush(self._backlog, (worst[0], worst[1], worst[2]))
            else:
                heapq.heappush(self._backlog, (rank, sequence, item))

    def enqueue_many(
        self,
        items: Sequence[tuple[T, ExecutionPriority]],
    ) -> None:
        """Adiciona vários itens mantendo a mesma semântica de ``enqueue``."""
        for item, priority in items:
            self.enqueue(item, priority)

    def pop_next(self) -> T | None:
        """Retira o próximo item pronto e promove o melhor backlog disponível."""
        with self._lock:
            if not self._ready:
                return None
            _, _, item = heapq.heappop(self._ready)
            self._promote_backlog()
            return item

    def pending(self) -> tuple[T, ...]:
        """Devolve todos os itens pendentes em ordem efectiva de prioridade."""
        with self._lock:
            ordered = sorted(
                [*self._ready, *self._backlog],
                key=lambda entry: (entry[0], entry[1]),
            )
            return tuple(entry[2] for entry in ordered)

    def clear(self) -> tuple[T, ...]:
        """Remove e devolve todos os itens ainda pendentes."""
        with self._lock:
            items = self.pending()
            self._ready.clear()
            self._backlog.clear()
            return items

    def snapshot(self) -> QueueSnapshot:
        """Obtém uma fotografia consistente das camadas da fila."""
        with self._lock:
            return QueueSnapshot(
                ready=len(self._ready),
                backlog=len(self._backlog),
                total=len(self._ready) + len(self._backlog),
            )

    def _promote_backlog(self) -> None:
        if not self._backlog:
            return
        if self._max_ready is not None and len(self._ready) >= self._max_ready:
            return
        entry = heapq.heappop(self._backlog)
        heapq.heappush(self._ready, entry)


def priority_for_plan(
    plan: ExecutionPlan,
    priorities: dict[str, ExecutionPriority] | None = None,
) -> ExecutionPriority:
    """Resolve a prioridade de um ``ExecutionPlan`` de forma determinística."""
    return (priorities or {}).get(plan.task_id, ExecutionPriority.NORMAL)


__all__ = ["MultilayerExecutionQueue", "QueueItem", "QueueSnapshot", "priority_for_plan"]
