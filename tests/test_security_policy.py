"""Testes do motor de política de segurança (Fase 8.8).

Valida o modelo do hardening 09 (principal -> project -> action ->
policy -> decision) com a regra registada: **exact-match por acção**, com
negação por omissão, validação de entrada e conversão da negação no erro
taxonómico da 8.2.
"""

import pytest

from wsai2.core.errors import PermissionError, ValidationError
from wsai2.security import PolicyDecision, PolicyEngine, Principal, denied_decision


def test_decide_concede_acao_exacta() -> None:
    """Uma acção concedida exactamente deve ser autorizada."""
    motor = PolicyEngine({"alice": ("execute", "code.run")})
    decisao = motor.decide("alice", "proj-1", "execute")
    assert decisao.allowed is True
    assert decisao.action == "execute"
    assert decisao.principal == "alice"
    assert decisao.project_id == "proj-1"
    assert "concedida" in decisao.reason


def test_diferencas_de_casas_nao_concedem() -> None:
    """O exact-match deve distinguir variações (ex.: 'Execute' != 'execute')."""
    motor = PolicyEngine({"alice": ("Execute",)})
    assert not motor.decide("alice", "proj-1", "execute").allowed


def test_acao_nao_explicitamente_concedida_e_negada() -> None:
    """Uma acção não declarada deve ser negada (negação por omissão)."""
    motor = PolicyEngine({"alice": ("code.run",)})
    decisao = motor.decide("alice", "proj-1", "execute")
    assert decisao.allowed is False
    assert "não concedida" in decisao.reason


def test_principal_desconhecido_e_negado() -> None:
    """Um principal sem qualquer permissão deve ser negado."""
    decisao = PolicyEngine().decide("bob", "proj-1", "execute")
    assert decisao.allowed is False


def test_principal_vazio_levanta_validation_error() -> None:
    """A decisão exige um principal não vazio."""
    with pytest.raises(ValidationError) as erro:
        PolicyEngine().decide("", "proj-1", "execute")
    assert erro.value.code == "wsai.security.principal"


def test_projecto_vazio_levanta_validation_error() -> None:
    """A decisão exige um projecto não vazio."""
    with pytest.raises(ValidationError) as erro:
        PolicyEngine({"alice": ("execute",)}).decide("alice", "", "execute")
    assert erro.value.code == "wsai.security.project"


def test_grant_acumula_permissoes() -> None:
    """``grant`` deve somar acções, não substituir as existentes."""
    motor = PolicyEngine({"alice": ("execute",)})
    motor.grant("alice", ("code.run",))
    assert motor.decide("alice", "p", "execute").allowed
    assert motor.decide("alice", "p", "code.run").allowed


def test_decide_principal_usa_id_e_projecto_do_principal() -> None:
    """``decide_principal`` deve delegar no portador Principal."""
    motor = PolicyEngine({"alice": ("execute",)})
    principal = Principal(id="alice", project_id="proj-9", permissions=("execute",))
    decisao = motor.decide_principal(principal, "execute")
    assert decisao.allowed is True
    assert decisao.principal == "alice"
    assert decisao.project_id == "proj-9"


def test_decisao_e_imutavel() -> None:
    """Uma decisão de política não deve ser modificável (frozen)."""
    decisao = PolicyDecision(
        action="execute",
        principal="alice",
        project_id="p",
        allowed=True,
        reason="ok",
    )
    with pytest.raises(Exception):
        decisao.allowed = False  # type: ignore[misc]


def test_denied_decision_devolve_permission_error_taxonico() -> None:
    """A negação deve converter-se no erro da taxonomia (8.2)."""
    motor = PolicyEngine({"alice": ("other",)})
    decisao = motor.decide("alice", "proj-1", "execute")
    erro = denied_decision(decisao)
    assert isinstance(erro, PermissionError)
    assert erro.code == "wsai.permission"
    assert erro.details["action"] == "execute"
    assert erro.details["principal"] == "alice"
    assert erro.details["project_id"] == "proj-1"


def test_principal_resumo_textual() -> None:
    """O principal deve expor um resumo textual com o projecto."""
    principal = Principal(id="alice", project_id="p-2")
    resumo = principal.summary
    assert "alice" in resumo
    assert "p-2" in resumo
    assert principal.has_project is True