"""Ciclo de vida de extensões (hardening 02 — Fase 8.6).

Em 8.1 declarou-se a taxonomia de estados (``ExtensionLifecycleState``);
esta unidade implementa a **máquina de transições** coerente com o
diagrama do CORE_HARDENING_PLAN:

    DISCOVERED → VALIDATED → REGISTERED → INITIALIZING → READY
                                          ↓
                                      RUNNING
                                          ↓
                                 DEGRADED / FAILED
                                          ↓
                                  STOPPING → STOPPED

A máquina **não executa side effects** no sistema (não lança, não
descarrega addons) — valida e produz o novo contrato. A regra "a falha
de um addon não pode derrubar o Core" materializa-se aqui: toda a
transição inválida é um erro observável (``ValidationError``) e nunca
altera estado global fora de quem a invoca.
"""

from __future__ import annotations

from dataclasses import replace

from wsai2.core.public import ValidationError

from .base import ExtensionContract, ExtensionLifecycleState

# Diagrama de transições válidas por estado de origem.
_DIAGRAMA: dict[ExtensionLifecycleState, tuple[ExtensionLifecycleState, ...]] = {
    ExtensionLifecycleState.DISCOVERED: (
        ExtensionLifecycleState.VALIDATED,
        ExtensionLifecycleState.FAILED,
    ),
    ExtensionLifecycleState.VALIDATED: (
        ExtensionLifecycleState.REGISTERED,
        ExtensionLifecycleState.FAILED,
    ),
    ExtensionLifecycleState.REGISTERED: (
        ExtensionLifecycleState.INITIALIZING,
        ExtensionLifecycleState.FAILED,
    ),
    ExtensionLifecycleState.INITIALIZING: (
        ExtensionLifecycleState.READY,
        ExtensionLifecycleState.FAILED,
    ),
    ExtensionLifecycleState.READY: (
        ExtensionLifecycleState.RUNNING,
        ExtensionLifecycleState.STOPPING,
        ExtensionLifecycleState.FAILED,
    ),
    ExtensionLifecycleState.RUNNING: (
        ExtensionLifecycleState.DEGRADED,
        ExtensionLifecycleState.FAILED,
        ExtensionLifecycleState.STOPPING,
    ),
    ExtensionLifecycleState.DEGRADED: (
        ExtensionLifecycleState.READY,
        ExtensionLifecycleState.FAILED,
        ExtensionLifecycleState.STOPPING,
    ),
    ExtensionLifecycleState.FAILED: (
        ExtensionLifecycleState.STOPPING,
    ),
    ExtensionLifecycleState.STOPPING: (
        ExtensionLifecycleState.STOPPED,
        ExtensionLifecycleState.FAILED,
    ),
    ExtensionLifecycleState.STOPPED: (),
}


def valid_transitions(
    estado: ExtensionLifecycleState,
) -> tuple[ExtensionLifecycleState, ...]:
    """Estados para os quais é válido transitar a partir de ``estado``."""
    return _DIAGRAMA.get(estado, ())


def can_transition(
    origem: ExtensionLifecycleState,
    destino: ExtensionLifecycleState,
) -> bool:
    """Indica se a transição ``origem -> destino`` é permitida."""
    return destino in valid_transitions(origem)


def transition(
    contrato: ExtensionContract,
    destino: ExtensionLifecycleState,
) -> ExtensionContract:
    """Move um contrato para ``destino``, validando a transição.

    Devolve um **novo** contrato (o original permanece imutável) com o
    estado de lifecycle actualizado.

    Args:
        contrato: extensão no estado de origem.
        destino: estado de destino pretendido.

    Returns:
        Um novo contrato com o novo estado.

    Raises:
        ValidationError: se a transição não for permitida.
    """
    if not can_transition(contrato.lifecycle, destino):
        raise ValidationError(
            f"transição inválida: {contrato.lifecycle.value} -> {destino.value}",
            code="wsai.extension.lifecycle",
            details={
                "origem": contrato.lifecycle.value,
                "destino": destino.value,
            },
        )
    return replace(contrato, lifecycle=destino)


__all__ = ["can_transition", "transition", "valid_transitions"]