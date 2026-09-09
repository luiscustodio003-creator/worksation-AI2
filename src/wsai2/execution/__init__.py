"""Subsistema de Políticas de Execução do WorkStation AI 2.

Centraliza no Runtime Engine as políticas de execução (hardening 06 do
CORE_HARDENING_PLAN): timeout, cancelamento cooperativo e recuperação —
para que os addons não inventem mecanismos incompatíveis.

Composição sobre as unidades anteriores da Fase 8: o ``ExecutionContext``
(8.2) fornece a deadline e o token de cancelamento; o ``ResourceGovernor``
(8.3) reserva o orçamento durante a execução. O agendamento e o gestor de
execução pertencem à unidade 8.5.
"""

from .base import RecoveryPolicy, RetryAttempt, TimeoutPolicy
from .runner import (
    DeadlineGuard,
    execute_with_policies,
    run_with_recovery,
    run_with_timeout,
)

# Contrato público da fronteira de execução (KERNEL-05): a superfície
# sancionada é o `__all__` abaixo, congelada por teste de contrato.
EXECUTION_CONTRACT_VERSION = "1.0"

__all__ = [
    "DeadlineGuard",
    "RecoveryPolicy",
    "RetryAttempt",
    "TimeoutPolicy",
    "execute_with_policies",
    "run_with_recovery",
    "run_with_timeout",
]