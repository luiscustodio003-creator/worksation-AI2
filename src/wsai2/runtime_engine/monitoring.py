"""Monitorização contínua de execuções do Runtime Engine.

Completa a observabilidade da unidade 8.5: além dos relatórios **pós-facto**
(``ExecutionReport``/``SchedulerReport``), o ``ExecutionMonitor`` observa a
execução **enquanto decorre** — regista o estado em curso de cada execução
(execution_id, tarefa, passo actual e tempo decorrido) e de cada
agendamento, permitindo interrogar ``snapshot()`` a qualquer momento, de
outra thread, sem esperar pelo relatório final.

Responsabilidades:

- manter o estado em curso de cada execução do ``RuntimeManager``;
- reter os relatórios finais (``ExecutionReport``) por execução;
- reter o último relatório de agendamento (``SchedulerReport``);
- expor ``snapshot()`` com acesso seguro para leitura concorrente.

A integração é **aditiva e opcional**: quando o ``RuntimeManager`` ou o
``Scheduler`` são usados sem ``monitor``, o comportamento é exactamente o de
antes. Fora de âmbito: a medição de recursos do sistema (CPU/RAM/GPU)
pertence ao Runtime Intelligence (``wsai2.runtime``); este módulo observa
apenas o progresso e o tempo de execução dos planos.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from .base import ExecutionReport

if TYPE_CHECKING:
    from .base import SchedulerReport


@dataclass(frozen=True)
class ExecutionSnapshot:
    """Estado em curso de uma execução num dado momento.

    Attributes:
        execution_id: identificador da execução (do contexto).
        task_id: identificador da tarefa (do plano).
        running: True enquanto a execução ainda não terminou.
        started_at: instante monotónico do arranque (relógio do monitor).
        elapsed: tempo decorrido desde o arranque, no momento da leitura.
        current_step: índice do passo em execução (-1 se ainda nenhum).
        current_step_name: descrição do passo em execução ("" se nenhum).
    """

    execution_id: str
    task_id: str
    running: bool
    started_at: float
    elapsed: float
    current_step: int
    current_step_name: str


@dataclass(frozen=True)
class MonitorSnapshot:
    """Fotografia do monitor num dado momento.

    Attributes:
        running: execuções em curso no momento da leitura.
        finished: relatórios de execuções já concluídas.
        started: total de execuções iniciadas.
        completed: total de execuções concluídas (igual a len(finished)).
        schedule_started_at: instante monotónico do agendamento em curso.
        last_schedule: último relatório de agendamento concluído (se houver).
    """

    running: tuple[ExecutionSnapshot, ...]
    finished: tuple[ExecutionReport, ...]
    started: int
    completed: int
    schedule_started_at: float | None
    last_schedule: SchedulerReport | None = None


@dataclass
class _RunState:
    """Estado interno de uma execução em curso (mutável, sob o trinco)."""

    execution_id: str
    task_id: str
    started_at: float
    current_step: int = -1
    current_step_name: str = ""


class ExecutionMonitor:
    """Regista e expõe o estado em curso de execuções e agendamentos.

    A instância é partilhada entre quem executa (``RuntimeManager``/
    ``Scheduler``) e quem observa (consumidores de ``snapshot()``); o acesso
    é protegido por um trinco para permitir a leitura de outra thread
    enquanto a execução decorre.
    """

    def __init__(self, *, clock: Callable[[], float] = time.monotonic) -> None:
        """Cria um monitor de execuções.

        Args:
            clock: relógio monotónico para medir durações (injectável).
        """
        self._clock = clock
        self._trinco = threading.Lock()
        self._em_curso: dict[str, _RunState] = {}
        self._concluidas: list[ExecutionReport] = []
        self._iniciadas = 0
        self._agendamento_inicio: float | None = None
        self._ultimo_agendamento: SchedulerReport | None = None

    def on_execution_started(self, execution_id: str, task_id: str) -> None:
        """Regista o arranque de uma execução."""
        with self._trinco:
            self._iniciadas += 1
            self._em_curso[execution_id] = _RunState(
                execution_id=execution_id,
                task_id=task_id,
                started_at=self._clock(),
            )

    def on_step_started(self, execution_id: str, index: int, step_name: str) -> None:
        """Actualiza o passo em execução de uma execução em curso."""
        with self._trinco:
            estado = self._em_curso.get(execution_id)
            if estado is None:
                return
            estado.current_step = index
            estado.current_step_name = step_name

    def on_execution_finished(self, report: ExecutionReport) -> None:
        """Retira a execução do estado em curso e guarda o relatório."""
        with self._trinco:
            self._em_curso.pop(report.execution_id, None)
            self._concluidas.append(report)

    def on_schedule_started(self) -> None:
        """Regista o início de um agendamento."""
        with self._trinco:
            self._agendamento_inicio = self._clock()

    def on_schedule_finished(self, report: SchedulerReport) -> None:
        """Regista o relatório do agendamento concluído."""
        with self._trinco:
            self._ultimo_agendamento = report
            self._agendamento_inicio = None

    def snapshot(self) -> MonitorSnapshot:
        """Fotografia actual: execuções em curso, concluídas e contagens.

        A leitura é segura para chamada concorrente com a execução.
        """
        agora = self._clock()
        with self._trinco:
            em_curso = tuple(
                ExecutionSnapshot(
                    execution_id=estado.execution_id,
                    task_id=estado.task_id,
                    running=True,
                    started_at=estado.started_at,
                    elapsed=max(0.0, agora - estado.started_at),
                    current_step=estado.current_step,
                    current_step_name=estado.current_step_name,
                )
                for estado in self._em_curso.values()
            )
            return MonitorSnapshot(
                running=em_curso,
                finished=tuple(self._concluidas),
                started=self._iniciadas,
                completed=len(self._concluidas),
                schedule_started_at=self._agendamento_inicio,
                last_schedule=self._ultimo_agendamento,
            )


__all__ = ["ExecutionMonitor", "ExecutionSnapshot", "MonitorSnapshot"]