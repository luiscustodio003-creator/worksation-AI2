"""Testes do isolamento de projectos (Fase 8.8 — hardening 10).

Valida que ``project_id`` é exigido na fronteira e que o acesso cruzado
entre projectos levanta o erro taxonómico da 8.2 sem nunca aceder dados.
"""

import pytest

from wsai2.core.errors import ProjectIsolationError, ValidationError
from wsai2.security import assert_same_project, require_project


def test_require_project_aceita_identificador_válido() -> None:
    """Um project_id preenchido deve passar a fronteira."""
    assert require_project("proj-1") == "proj-1"


def test_require_project_normaliza_espacos() -> None:
    """Espaços em branco envolventes devem ser removidos."""
    assert require_project("  proj-1  ") == "proj-1"


@pytest.mark.parametrize("invalido", ["", "   "])
def test_require_project_rejeita_vazio(invalido: str) -> None:
    """Projecto vazio ou em branco deve ser rejeitado."""
    with pytest.raises(ValidationError) as erro:
        require_project(invalido)
    assert erro.value.code == "wsai.security.project"


def test_mesmo_projecto_passa_sem_erro() -> None:
    """Dois identificadores iguais ao caso exacto não violam a fronteira."""
    assert_same_project("p-1", "p-1")
    assert_same_project("", "")
    assert_same_project("p-1", "")


def test_projectos_diferentes_levantam_project_isolation_error() -> None:
    """Acesso cruzado entre projectos deve ser impedido."""
    with pytest.raises(ProjectIsolationError) as erro:
        assert_same_project("proj-a", "proj-b")
    assert erro.value.code == "wsai.project_isolation"
    assert erro.value.details == {"esperado": "proj-a", "actual": "proj-b"}