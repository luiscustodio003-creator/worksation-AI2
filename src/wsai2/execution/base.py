"""Contratos das políticas de execução (hardening 06 do CORE_HARDENING_PLAN).

Este módulo contém apenas definições de tipos e dataclasses — não
implementa a execução concreta (essa fica em ``runner.py``). Garante que
as políticas centrais do Runtime Engine (timeout, recuperação) dependem
de contratos estáveis, sem duplicar os mecanismos do núcleo (o
``ExecutionContext`` da 8.2 já transporta a deadline e o token de
cancelamento cooperativo).

Os contratos aqui definidos centralizam a configuração das políticas:
os addons não devem inventar mecanismos incompatíveis — devem consumir
estas políticas.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from wsai2.core.errors import ValidationError


@dataclass(frozen=True)
class TimeoutPolicy:
    """Limite temporal de uma execução.

    Define uma única via de limite: ``duration_seconds`` (duração desde o
    início) ou ``deadline`` (instante absoluto em ``time.monotonic``).
    Sem qualquer das vias, a política é ilimitada (sem timeout).

    Quando combinada com um ``ExecutionContext``, o limite efectivo é o
    mais curto entre a política e a deadline do contexto (``runner.py``).
    """

    duration_seconds: float | None = None
    deadline: float | None = None

    def __post_init__(self) -> None:
        """Valida a política no momento da criação."""
        if self.duration_seconds is not None and self.deadline is not None:
            raise ValidationError("definir apenas uma via de limite temporal")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValidationError("a duração do timeout não pode ser negativa")

    @property
    def is_limited(self) -> bool:
        """Indica se a política impõe um limite temporal."""
        return self.duration_seconds is not None or self.deadline is not None

    def absolute_deadline(self, now: float | None = None) -> float | None:
        """Deadline absoluta em ``time.monotonic``, ou ``None`` se ilimitada.

        Args:
            now: instante actual (injectável para testes); usa
                ``time.monotonic()`` se omisso.
        """
        if self.deadline is not None:
            return self.deadline
        if self.duration_seconds is not None:
            actual = time.monotonic() if now is None else now
            return actual + self.duration_seconds
        return None


@dataclass(frozen=True)
class RecoveryPolicy:
    """Política de recuperação por tentativas (retry).

    Repete a execução até ``max_attempts`` quando o erro levantado for de
    um tipo declarado em ``retry_error_types``. O atraso entre tentativas
    é ``base_delay_seconds * backoff_factor**k`` (fixo com factor 1.0;
    exponencial com factor > 1.0).

    Por omissão ``retry_error_types`` fica vazio — sem repetição
    automática (opt-in explícito), evitando repetir falhas por engano.
    """

    max_attempts: int = 1
    base_delay_seconds: float = 0.0
    backoff_factor: float = 1.0
    retry_error_types: tuple[type[BaseException], ...] = ()

    def __post_init__(self) -> None:
        """Valida a política no momento da criação."""
        if self.max_attempts < 1:
            raise ValidationError("max_attempts tem de ser >= 1")
        if self.base_delay_seconds < 0:
            raise ValidationError("base_delay_seconds não pode ser negativa")
        if self.backoff_factor < 1.0:
            raise ValidationError("backoff_factor tem de ser >= 1.0")

    @property
    def retry_count(self) -> int:
        """Número máximo de repetições após a primeira tentativa."""
        return self.max_attempts - 1

    def is_retryable(self, error: BaseException) -> bool:
        """Indica se o erro é do tipo declarado como repetível."""
        return any(isinstance(error, expected) for expected in self.retry_error_types)

    def delay_for_attempt(self, number: int) -> float:
        """Atraso aplicado antes da tentativa ``number`` (1-based)."""
        if number <= 1:
            return 0.0
        return self.base_delay_seconds * (self.backoff_factor ** (number - 2))


@dataclass(frozen=True)
class RetryAttempt:
    """Registo de uma tentativa de uma política de recuperação.

    Attributes:
        number: número da tentativa (1-based).
        error: erro levantado, ou ``None`` em tentativa bem-sucedida.
        details: metadados opacos da tentativa.
    """

    number: int
    error: BaseException | None = None
    details: dict[str, str] = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        """Indica se a tentativa não levantou erro."""
        return self.error is None

    @property
    def summary(self) -> str:
        """Resumo textual da tentativa para apresentação."""
        if self.succeeded:
            return f"tentativa {self.number}: sucesso"
        return f"tentativa {self.number}: erro {type(self.error).__name__}"


__all__ = [
    "RecoveryPolicy",
    "RetryAttempt",
    "TimeoutPolicy",
]