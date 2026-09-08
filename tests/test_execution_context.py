"""Testes do Execution Context (Fase 8.2).

Valida o transporte consistente dos dados de execução: identidade,
deadline, cancelamento cooperativo, budget e prioridade, incluindo a
imutabilidade e as validações à criação.
"""

import time

import pytest

from wsai2.core import (
    CancellationError,
    CancellationToken,
    ExecutionContext,
    ExecutionPriority,
    ValidationError,
)
from wsai2.extension import ResourceLimit


def _contexto(**kwargs: object) -> ExecutionContext:
    """Constrói um contexto de execução de teste com valores válidos."""
    valores: dict[str, object] = {"execution_id": "exec-1", "task_id": "task-1"}
    valores.update(kwargs)
    return ExecutionContext(**valores)  # type: ignore[arg-type]


def test_contexto_valido_com_todos_os_campos() -> None:
    """Um contexto completo deve preservar todos os valores."""
    limite = ResourceLimit(name="memory_mb", value=512.0)
    token = CancellationToken()
    ctx = _contexto(
        project_id="proj-1",
        deadline=time.monotonic() + 60.0,
        cancellation=token,
        budget=(limite,),
        priority=ExecutionPriority.HIGH,
        metadata={"origem": "teste"},
    )

    assert ctx.execution_id == "exec-1"
    assert ctx.task_id == "task-1"
    assert ctx.project_id == "proj-1"
    assert ctx.has_deadline is True
    assert ctx.cancellation is token
    assert ctx.budget == (limite,)
    assert ctx.priority is ExecutionPriority.HIGH
    assert ctx.metadata == {"origem": "teste"}


def test_contexto_defaults_aplicados() -> None:
    """Os campos opcionais devem ter os valores predefinidos documentados."""
    ctx = _contexto()

    assert ctx.project_id == ""
    assert ctx.deadline is None
    assert ctx.cancellation is None
    assert ctx.budget == ()
    assert ctx.priority is ExecutionPriority.NORMAL
    assert ctx.metadata == {}


def test_contexto_imutavel() -> None:
    """Um contexto validado não deve ser modificável (frozen)."""
    ctx = _contexto()
    with pytest.raises(Exception):
        ctx.task_id = "task-2"  # type: ignore[misc]


def test_contexto_rejeita_execution_id_vazio() -> None:
    """Um execution_id vazio deve ser rejeitado com ValidationError."""
    with pytest.raises(ValidationError):
        _contexto(execution_id="")


def test_contexto_rejeita_task_id_vazio() -> None:
    """Um task_id vazio deve ser rejeitado com ValidationError."""
    with pytest.raises(ValidationError):
        _contexto(task_id="")


def test_contexto_rejeita_deadline_no_passado() -> None:
    """Uma deadline no passado deve ser rejeitada com ValidationError."""
    with pytest.raises(ValidationError):
        _contexto(deadline=time.monotonic() - 10.0)


def test_deadline_futura_expira_apos_limite() -> None:
    """Com deadline futura, o contexto deve reportar tempo restante e não expirado."""
    ctx = _contexto(deadline=time.monotonic() + 60.0)
    assert ctx.has_deadline is True
    assert ctx.is_expired is False
    assert ctx.remaining_seconds is not None
    assert ctx.remaining_seconds > 0


def test_sem_deadline_propriedades_inactivas() -> None:
    """Sem deadline, não deve haver limite nem expiração."""
    ctx = _contexto()
    assert ctx.has_deadline is False
    assert ctx.is_expired is False
    assert ctx.remaining_seconds is None


def test_cancellation_token_fluxo_completo() -> None:
    """O token deve registar o cancelamento e lançar o erro cooperativo."""
    token = CancellationToken()
    assert token.is_cancelled is False
    token.cancel()
    assert token.is_cancelled is True
    with pytest.raises(CancellationError):
        token.raise_if_cancelled()


def test_cancellation_token_sem_cancelamento_nao_lanca() -> None:
    """Sem cancelamento, raise_if_cancelled não deve lançar."""
    CancellationToken().raise_if_cancelled()


def test_contexto_encadeia_cancelamento_no_token() -> None:
    """O contexto deve delegar a validação do cancelamento no token."""
    token = CancellationToken()
    ctx = _contexto(cancellation=token)
    ctx.raise_if_cancelled()
    token.cancel()
    with pytest.raises(CancellationError):
        ctx.raise_if_cancelled()


def test_contexto_sem_token_nao_levanta() -> None:
    """Sem token, o contexto não deve levantar na validação de cancelamento."""
    _contexto().raise_if_cancelled()


def test_prioridades_previstas() -> None:
    """As prioridades devem cobrir o espectro low → critical."""
    assert {p.value for p in ExecutionPriority} == {
        "low",
        "normal",
        "high",
        "critical",
    }


def test_budget_reutiliza_resource_limit_da_extensao() -> None:
    """O budget deve aceitar limites declarados pela extensão (8.1)."""
    limite = ResourceLimit(name="cpu", value=2.0)
    ctx = _contexto(budget=(limite,))
    assert ctx.budget[0].name == "cpu"
    assert ctx.budget[0].value == 2.0


def test_resumo_textual_do_contexto() -> None:
    """O resumo deve conter a identidade da execução e da tarefa."""
    resumo = _contexto().summary
    assert "exec-1" in resumo
    assert "task-1" in resumo