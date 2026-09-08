"""Testes da máquina de lifecycle de extensões (Fase 8.6).

Valida as transições do diagrama do hardening 02, a imutabilidade do
contrato (cada transição devolve um novo contrato) e o isolamento de
falhas: transições inválidas são ``ValidationError`` observáveis, sem
efeitos laterais no sistema.
"""

from enum import Enum

import pytest

from wsai2.core.errors import ValidationError
from wsai2.extension import (
    ExtensionContract,
    ExtensionKind,
    ExtensionLifecycleState,
    can_transition,
    transition,
    valid_transitions,
)


def _contrato(estado: ExtensionLifecycleState) -> ExtensionContract:
    """Constrói um contrato de teste num estado de lifecycle dado."""
    return ExtensionContract(
        id="wsai.teste",
        name="Extensão de Teste",
        description="Extensão utilitária de teste.",
        kind=ExtensionKind.UTILITY,
        version="1.0.0",
        contract_version="1.0",
        lifecycle=estado,
    )


def test_sequencia_principal_completa() -> None:
    """O caminho feliz deve percorrer todo o diagrama até STOPPED."""
    contrato = _contrato(ExtensionLifecycleState.DISCOVERED)
    sequencia = [
        ExtensionLifecycleState.VALIDATED,
        ExtensionLifecycleState.REGISTERED,
        ExtensionLifecycleState.INITIALIZING,
        ExtensionLifecycleState.READY,
        ExtensionLifecycleState.RUNNING,
        ExtensionLifecycleState.DEGRADED,
        ExtensionLifecycleState.READY,
        ExtensionLifecycleState.STOPPING,
        ExtensionLifecycleState.STOPPED,
    ]
    for destino in sequencia:
        contrato = transition(contrato, destino)
        assert contrato.lifecycle is destino


def test_transicao_devolve_novo_contrato_sem_mutar_o_original() -> None:
    """Cada transição deve devolver um novo contrato (imutabilidade)."""
    original = _contrato(ExtensionLifecycleState.DISCOVERED)
    movido = transition(original, ExtensionLifecycleState.VALIDATED)
    assert movido is not original
    assert original.lifecycle is ExtensionLifecycleState.DISCOVERED
    assert movido.lifecycle is ExtensionLifecycleState.VALIDATED


def test_falha_entrada_e_permitida_a_partir_de_cada_estado() -> None:
    """A falha deve ser alcançável de todos os estados activos."""
    activos = [
        ExtensionLifecycleState.DISCOVERED,
        ExtensionLifecycleState.VALIDATED,
        ExtensionLifecycleState.REGISTERED,
        ExtensionLifecycleState.INITIALIZING,
        ExtensionLifecycleState.READY,
        ExtensionLifecycleState.RUNNING,
        ExtensionLifecycleState.DEGRADED,
        ExtensionLifecycleState.STOPPING,
    ]
    for estado in activos:
        assert can_transition(estado, ExtensionLifecycleState.FAILED)


def test_ready_recupera_de_failed_via_stopping() -> None:
    """O estado FAILED deve ser escapável apenas pelo caminho de paragem."""
    contrato = _contrato(ExtensionLifecycleState.FAILED)
    assert not can_transition(contrato.lifecycle, ExtensionLifecycleState.READY)
    contrato = transition(contrato, ExtensionLifecycleState.STOPPING)
    assert contrato.lifecycle is ExtensionLifecycleState.STOPPING


def test_estado_stopped_e_terminal() -> None:
    """O estado STOPPED não deve permitir transições de saída."""
    assert valid_transitions(ExtensionLifecycleState.STOPPED) == ()


def test_estado_ready_permite_running_e_stopping() -> None:
    """A partir de READY devem existir saídas operacionais e de paragem."""
    permissiveis = valid_transitions(ExtensionLifecycleState.READY)
    assert ExtensionLifecycleState.RUNNING in permissiveis
    assert ExtensionLifecycleState.STOPPING in permissiveis


def test_transicao_invalida_ergue_validation_error_isolada() -> None:
    """Uma transição inválida deve falhar sem alterar nenhum estado."""
    contrato = _contrato(ExtensionLifecycleState.DISCOVERED)
    with pytest.raises(ValidationError) as erro:
        transition(contrato, ExtensionLifecycleState.READY)
    assert erro.value.code == "wsai.extension.lifecycle"
    assert contrato.lifecycle is ExtensionLifecycleState.DISCOVERED


def test_transicao_invalida_regista_origem_e_destino() -> None:
    """O erro deve descrever a origem e o destino da transição negada."""
    with pytest.raises(ValidationError) as erro:
        transition(
            _contrato(ExtensionLifecycleState.REGISTERED),
            ExtensionLifecycleState.RUNNING,
        )
    detalhes = erro.value.details
    assert detalhes["origem"] == "registered"
    assert detalhes["destino"] == "running"


def test_valid_transitions_sempre_do_mesmo_enum() -> None:
    """As transições devolvidas devem ser sempre estados do mesmo enum."""
    for estado in ExtensionLifecycleState:
        for destino in valid_transitions(estado):
            assert isinstance(destino, Enum)
            assert destino in ExtensionLifecycleState


def test_diagrama_cobre_todos_os_estados_declarados() -> None:
    """Todos os estados do enum devem ter correspondência no diagrama."""
    for estado in ExtensionLifecycleState:
        valid_transitions(estado)  # não pode levantar para nenhum estado