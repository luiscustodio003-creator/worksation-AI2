"""Motores das políticas de execução (hardening 06 do CORE_HARDENING_PLAN).

Centraliza no Runtime Engine a aplicação real de timeout, cancelamento
cooperativo (checkpoints) e recuperação (retry), compondo com o
``ExecutionContext`` (8.2) e o ``ResourceGovernor`` (8.3) já existentes.

Fronteiras desta unidade:
- o núcleo ``wsai2.core`` permanece folha — o token nele definido é
  thread-agnostic; a gestão de threads e os relógios de enforcement são
  responsabilidade **deste** módulo (camada de políticas da Fase 8);
- o agendamento e o gestor de execução pertencem à unidade 8.5;
- uma thread "fugitiva" (que ignore a deadline) não é morta — seria
  inseguro; levanta-se `TimeoutError` e o código cooperativo deve
  observar o token/deadline para terminar.
"""

from __future__ import annotations

import queue
import threading
import time
from functools import partial
from typing import TYPE_CHECKING, Any, Callable

from wsai2.core.context import ExecutionContext
from wsai2.core.errors import TimeoutError

from .base import RecoveryPolicy, TimeoutPolicy, RetryAttempt

if TYPE_CHECKING:
    from wsai2.resource import ResourceGovernor, ResourceAllocation

_MENSAGEM_TIMEOUT = "tempo de execução excedido"
_CODIGO_TIMEOUT = "wsai.timeout.exceeded"


def _checkpoint(context: ExecutionContext | None) -> None:
    """Valida cancelamento cooperativo e deadline num ponto de controlo.

    Levanta ``CancellationError`` se o token estiver cancelado e
    ``TimeoutError`` se a deadline já tiver sido ultrapassada.
    """
    if context is None:
        return
    context.raise_if_cancelled()
    if context.is_expired:
        raise TimeoutError(_MENSAGEM_TIMEOUT, code=_CODIGO_TIMEOUT)


class DeadlineGuard:
    """Relógio monotónico que enforça uma deadline.

    Permite medir o tempo restante e detectar a expiração de forma
    determinística, com relógio injectável para testes.
    """

    def __init__(self, deadline: float | None, *, clock: Callable[[], float] = time.monotonic) -> None:
        """Cria um guard de deadline.

        Args:
            deadline: instante absoluto em ``time.monotonic`` (ou ``None``
                para sem limite).
            clock: função de relógio (injectável para testes).
        """
        self._deadline = deadline
        self._clock = clock

    @property
    def deadline(self) -> float | None:
        """Instante absoluto da deadline, ou ``None`` sem limite."""
        return self._deadline

    @property
    def now(self) -> float:
        """Instante actual segundo o relógio do guard."""
        return self._clock()

    @property
    def remaining_seconds(self) -> float | None:
        """Tempo restante até à deadline, ou ``None`` sem limite."""
        if self._deadline is None:
            return None
        return max(0.0, self._deadline - self._clock())

    @property
    def is_expired(self) -> bool:
        """Indica se a deadline já foi ultrapassada."""
        if self._deadline is None:
            return False
        return self._clock() >= self._deadline

    def raise_if_expired(self) -> None:
        """Levanta ``TimeoutError`` se a deadline já tiver expirado."""
        if self.is_expired:
            raise TimeoutError(_MENSAGEM_TIMEOUT, code=_CODIGO_TIMEOUT)


def _resolve_deadline(
    timeout: TimeoutPolicy | None,
    context: ExecutionContext | None,
) -> float | None:
    """Resolve a deadline efectiva (a mais curta entre política e contexto)."""
    deadlines: list[float] = []
    if timeout is not None and timeout.is_limited:
        deadlines.append(timeout.absolute_deadline())
    if context is not None and context.has_deadline:
        deadlines.append(context.deadline)  # type: ignore[arg-type]
    if not deadlines:
        return None
    return min(deadlines)


def run_with_timeout(
    fn: Callable[[], Any],
    timeout: TimeoutPolicy | None = None,
    *,
    context: ExecutionContext | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> Any:
    """Executa ``fn`` com limite temporal, devolvendo o resultado.

    Sem limite efectivo (sem política nem deadline no contexto) executa no
    thread actual, sem sobrecarga. Com limite, executa num thread *worker*
    ``daemon`` e, se a deadline for excedida, levanta ``TimeoutError``.
    Erros levantados dentro de ``fn`` propagam-se tais quais (preservando
    o tipo) após o ``join``.

    Args:
        fn: função a executar (sem argumentos).
        timeout: política de timeout a aplicar (opcional).
        context: contexto de execução cuja deadline e cancelamento também
            se aplicam (opcional).
        clock: relógio monotónico (injectável para testes).

    Returns:
        O valor devolvido por ``fn``.

    Raises:
        TimeoutError: se a deadline for excedida (ou já estiver aquando do
            início).
        CancellationError: se o token do contexto estiver cancelado.
    """
    deadline = _resolve_deadline(timeout, context)
    if context is not None:
        _checkpoint(context)
    if deadline is None:
        return fn()
    guard = DeadlineGuard(deadline, clock=clock)
    guard.raise_if_expired()

    resultados: queue.Queue = queue.Queue(maxsize=1)

    def _alvo() -> None:
        try:
            resultados.put(("ok", fn()))
        except BaseException as error:  # noqa: BLE001 - transferência para o chamador
            resultados.put(("erro", error))

    worker = threading.Thread(target=_alvo, daemon=True, name="wsai-execution")
    worker.start()
    worker.join(timeout=guard.remaining_seconds)
    if worker.is_alive():
        raise TimeoutError(_MENSAGEM_TIMEOUT, code=_CODIGO_TIMEOUT)

    estado, valor = resultados.get_nowait()
    if estado == "erro":
        raise valor
    return valor


def run_with_recovery(
    fn: Callable[[], Any],
    policy: RecoveryPolicy,
    *,
    sleeper: Callable[[float], None] = time.sleep,
    history: list[RetryAttempt] | None = None,
) -> Any:
    """Executa ``fn`` com recuperação por tentativas.

    Repete até ``policy.max_attempts`` quando o erro for do tipo declarado
    como repetível. No fim das tentativas, **levanta o último erro**
    (preservando o tipo original).

    Args:
        fn: função a executar.
        policy: política de recuperação.
        sleeper: função de espera entre tentativas (injectável).
        history: lista opcional que recolhe os registos de cada tentativa.

    Returns:
        O valor devolvido por ``fn`` numa tentativa bem-sucedida.

    Raises:
        Exception: o último erro, quando as tentativas se esgotam (ou o
            primeiro erro não repetível).
    """
    ultimo: BaseException | None = None
    for numero in range(1, policy.max_attempts + 1):
        atraso = policy.delay_for_attempt(numero)
        if atraso > 0:
            sleeper(atraso)
        try:
            valor = fn()
            if history is not None:
                history.append(RetryAttempt(number=numero))
            return valor
        except Exception as erro:  # noqa: BLE001 - registado e re-lançado
            ultimo = erro
            if history is not None:
                history.append(RetryAttempt(number=numero, error=erro))
            if numero >= policy.max_attempts or not policy.is_retryable(erro):
                break
    if ultimo is None:
        raise TimeoutError("sem tentativas para recuperação", code=_CODIGO_TIMEOUT)
    raise ultimo


def execute_with_policies(
    fn: Callable[[], Any],
    *,
    context: ExecutionContext | None = None,
    timeout: TimeoutPolicy | None = None,
    recovery: RecoveryPolicy | None = None,
    governor: ResourceGovernor | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> Any:
    """Executa ``fn`` com as políticas centralizadas do Runtime Engine.

    Composição, por ordem:
    1. valida o cancelamento/deadline do contexto (checkpoint inicial);
    2. enforça o timeout efectivo (política e/ou deadline do contexto);
    3. aplica a recuperação (retry), se configurada;
    4. reserva o orçamento no ``ResourceGovernor`` quando fornecido e o
       contexto tiver budget — e liberta-o no fim (``finally``).

    Args:
        fn: função a executar.
        context: contexto de execução (cancelamento, deadline, budget).
        timeout: política de timeout adicional (opcional).
        recovery: política de recuperação (opcional).
        governor: governador de recursos (8.3) para reservar o budget.
        sleeper: função de espera entre tentativas (injectável).

    Returns:
        O valor devolvido por ``fn``.

    Raises:
        TimeoutError, CancellationError, ResourceError: conforme as
            políticas aplicadas; também os erros levantados por ``fn``.
    """
    if context is not None:
        _checkpoint(context)

    budget = context.budget if context is not None else ()
    alocacao = None
    if governor is not None and budget:
        alocacao = governor.allocate(context.execution_id, budget)

    def _com_controlo() -> Any:
        if context is not None:
            _checkpoint(context)
        return fn()

    alvo: Callable[[], Any] = _com_controlo
    if timeout is not None or (context is not None and context.has_deadline):
        alvo = partial(run_with_timeout, alvo, timeout=timeout, context=context)
    if recovery is not None:
        alvo = partial(run_with_recovery, alvo, recovery, sleeper=sleeper)

    try:
        return alvo()
    finally:
        if alocacao is not None:
            governor.release(alocacao.allocation_id)


__all__ = [
    "DeadlineGuard",
    "execute_with_policies",
    "run_with_recovery",
    "run_with_timeout",
]