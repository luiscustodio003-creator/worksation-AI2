"""Isolamento de projectos (hardening 10 — Fase 8.8).

O ``project_id`` já viaja no ``ExecutionContext`` (8.2); esta unidade dá
à fronteira o que faltava: verificação executável de que um acessor nunca
atravessa um projecto para outro **sem autorização explícita**.

As guardas são funções puras que apenas validam e levantam — nunca
acessam dados nem carregam recursos. O erro emitido é o taxonómico da
8.2 (`ProjectIsolationError`), que passa a ter aqui o primeiro emissor
real do repositório.
"""

from __future__ import annotations

from wsai2.core.errors import ProjectIsolationError, ValidationError


def require_project(project_id: str) -> str:
    """Exige um ``project_id`` não vazio.

    Args:
        project_id: identificador do projecto a validar.

    Returns:
        O próprio ``project_id`` (normalizado).

    Raises:
        ValidationError: se o projecto estiver vazio ou em branco.
    """
    if not project_id or not project_id.strip():
        raise ValidationError(
            "é obrigatório um project_id não vazio nesta fronteira",
            code="wsai.security.project",
        )
    return project_id.strip()


def assert_same_project(esperado: str, actual: str) -> None:
    """Garante que dois identificadores referem o mesmo projecto.

    Impede acesso cruzado entre projectos sem autorização explícita:
    se ambos os identificadores estiverem preenchidos e diferirem, a
    fronteira é violada.

    Args:
        esperado: projecto de contexto/requisito (ex.: do plano).
        actual: projecto observado (ex.: do recurso a aceder).

    Raises:
        ProjectIsolationError: se os projectos forem diferentes.
    """
    if esperado and actual and esperado != actual:
        raise ProjectIsolationError(
            "acesso cruzado entre projectos detectado",
            code="wsai.project_isolation",
            details={"esperado": esperado, "actual": actual},
        )


__all__ = ["assert_same_project", "require_project"]