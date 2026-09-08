"""Testes do registo de extensões (Fase 8.6).

Valida o padrão de catálogo (consultas, remoção) e as duas barreiras
antes do registo efectivo: unicidade de identidade e compatibilidade de
contrato com o núcleo (hardening 08) — rejeição **antes** de a extensão
ser executada. O estado de lifecycle é mantido no próprio contrato.
"""

import pytest

from wsai2.core.errors import ValidationError
from wsai2.extension import (
    ExtensionContract,
    ExtensionKind,
    ExtensionLifecycleState,
    ExtensionRegistry,
)
from wsai2.security import PolicyEngine


def _contrato(
    identidade: str = "wsai.teste",
    *,
    contract_version: str = "1.0",
    lifecycle: ExtensionLifecycleState = ExtensionLifecycleState.VALIDATED,
    permissions: tuple[str, ...] = (),
) -> ExtensionContract:
    """Constrói um contrato de teste pronto para registo."""
    return ExtensionContract(
        id=identidade,
        name="Extensão de Teste",
        description="Extensão utilitária de teste.",
        kind=ExtensionKind.UTILITY,
        version="1.0.0",
        contract_version=contract_version,
        lifecycle=lifecycle,
        permissions=permissions,
    )


def test_registar_marca_registered_e_preserva_identidade() -> None:
    """O registo deve mover o contrato para REGISTERED."""
    registo = ExtensionRegistry()
    contrato = registo.register(_contrato())
    assert contrato.lifecycle is ExtensionLifecycleState.REGISTERED
    assert registo.get("wsai.teste") is contrato
    assert registo.has("wsai.teste")


def test_registar_rejeita_identidade_duplicada() -> None:
    """Uma identidade segunda vez deve ser rejeitada."""
    registo = ExtensionRegistry()
    registo.register(_contrato("wsai.a"))
    with pytest.raises(ValidationError) as erro:
        registo.register(_contrato("wsai.a"))
    assert erro.value.code == "wsai.extension.duplicate"


def test_versao_suportada_por_defeito() -> None:
    """A versão suportada deve ser a constante da base por omissão."""
    assert ExtensionRegistry().supported_contract_version == "1.0"


def test_registar_rejeita_contrato_incompativel_antes_de_registar() -> None:
    """Um major distinto (contrato 2.x) deve ser rejeitado antes do registo."""
    registo = ExtensionRegistry()
    with pytest.raises(ValidationError) as erro:
        registo.register(
            _contrato(contract_version="2.0", lifecycle=ExtensionLifecycleState.VALIDATED)
        )
    assert erro.value.code == "wsai.extension.contract_incompatible"
    assert not registo.has("wsai.teste")


def test_registar_rejeita_versao_de_contrato_mal_formada() -> None:
    """Uma contract_version ilegível deve ser rejeitada à entrada."""
    registo = ExtensionRegistry()
    with pytest.raises(ValidationError) as erro:
        registo.register(
            _contrato(contract_version="1.0.0-beta")
        )
    assert erro.value.code == "wsai.extension.contract_version"


def test_registar_aceita_menor_inferior_ao_suportado() -> None:
    """Um minor inferior dentro do mesmo major deve ser aceite."""
    registo = ExtensionRegistry()
    contrato = registo.register(_contrato(contract_version="1.0"))
    assert contrato.lifecycle is ExtensionLifecycleState.REGISTERED
    outro = registo.register(_contrato("wsai.outro", contract_version="1.2"))
    assert registo.has("wsai.outro")


def test_registar_exige_estado_validated() -> None:
    """Registar uma extensão que não esteja VALIDATED deve falhar."""
    registo = ExtensionRegistry()
    with pytest.raises(ValidationError) as erro:
        registo.register(_contrato(lifecycle=ExtensionLifecycleState.DISCOVERED))
    assert erro.value.code == "wsai.extension.lifecycle"
    assert not registo.has("wsai.teste")


def test_consultas_sobre_o_catalogo() -> None:
    """get/has/all/len devem reflectir fielmente o catálogo."""
    registo = ExtensionRegistry()
    assert not registo.has("wsai.a")
    assert registo.get("wsai.a") is None
    registo.register(_contrato("wsai.a"))
    registo.register(_contrato("wsai.b"))
    assert registo.has("wsai.a")
    assert registo.get("wsai.b").id == "wsai.b"  # type: ignore[union-attr]
    assert len(registo) == 2
    assert [c.id for c in registo.all()] == ["wsai.a", "wsai.b"]


def test_unregister_remove_do_catalogo() -> None:
    """Unregister deve remover e devolver True apenas quando existia."""
    registo = ExtensionRegistry()
    registo.register(_contrato("wsai.a"))
    assert registo.unregister("wsai.a")
    assert not registo.has("wsai.a")
    assert not registo.unregister("wsai.a")
    assert len(registo) == 0


def test_state_levanta_para_extensao_desconhecida() -> None:
    """Consultar o estado de uma extensão ausente deve falhar."""
    registo = ExtensionRegistry()
    with pytest.raises(ValidationError) as erro:
        registo.state("wsai.ausente")
    assert erro.value.code == "wsai.extension.unknown"


def test_transition_state_move_e_persiste_estado() -> None:
    """A transição delegada no registo deve persistir o novo estado."""
    registo = ExtensionRegistry()
    registo.register(_contrato("wsai.a"))
    movido = registo.transition_state("wsai.a", ExtensionLifecycleState.INITIALIZING)
    assert movido.lifecycle is ExtensionLifecycleState.INITIALIZING
    assert registo.state("wsai.a") is ExtensionLifecycleState.INITIALIZING


def test_transition_state_levanta_para_extensao_desconhecida() -> None:
    """Transitar uma extensão ausente deve falhar."""
    registo = ExtensionRegistry()
    with pytest.raises(ValidationError) as erro:
        registo.transition_state("wsai.ausente", ExtensionLifecycleState.REGISTERED)
    assert erro.value.code == "wsai.extension.unknown"


def test_registrar_concede_permissions_como_grants_exactos() -> None:
    """As permissões declaradas devem tornar-se acções concedidas à extensão."""
    motor = PolicyEngine()
    registo = ExtensionRegistry()
    registo.register(
        _contrato(permissions=("execute", "code.run")),
        policy=motor,
    )
    decisao = motor.decide("wsai.teste", "proj-1", "execute")
    assert decisao.allowed is True
    assert motor.decide("wsai.teste", "proj-1", "code.run").allowed is True
    assert motor.decide("wsai.teste", "proj-1", "não_declarada").allowed is False
    assert motor.decide("outra.extensao", "proj-1", "execute").allowed is False


def test_registrar_sem_policy_nao_concede_nada() -> None:
    """Sem motor, o registo não deve materializar permissões na política."""
    motor = PolicyEngine()
    ExtensionRegistry().register(_contrato(permissions=("execute",)))
    assert motor.decide("wsai.teste", "proj-1", "execute").allowed is False


def test_registrar_aceite_nao_depende_de_policy() -> None:
    """A política é uma entidade distinta: registrar não é autorizar."""
    registo = ExtensionRegistry()
    contrato = registo.register(
        _contrato(permissions=("execute",)),
        policy=PolicyEngine(),
    )
    assert contrato.lifecycle is ExtensionLifecycleState.REGISTERED
    assert registo.has("wsai.teste")


def test_registo_nao_sai_do_estado_activo_por_transicao_invalida() -> None:
    """Uma transição negada não deve corromper o catálogo."""
    registo = ExtensionRegistry()
    registo.register(_contrato("wsai.a"))
    with pytest.raises(ValidationError):
        registo.transition_state("wsai.a", ExtensionLifecycleState.STOPPED)
    assert registo.state("wsai.a") is ExtensionLifecycleState.REGISTERED