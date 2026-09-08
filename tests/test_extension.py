"""Testes do Extension Contract do WorkStation AI 2.

Valida o contrato mínimo declarativo das extensões: construção,
validação à criação, imutabilidade, defaults, enums (tipos e lifecycle)
e resumo textual.
"""

import pytest

from wsai2.extension import (
    ExtensionContract,
    ExtensionKind,
    ExtensionLifecycleState,
    ResourceLimit,
)


def _contracto(
    *,
    identifier: str = "wsai.foo",
    name: str = "Foo Extensão",
    kind: ExtensionKind = ExtensionKind.UTILITY,
    version: str = "1.0.0",
    contract_version: str = "1.0",
    capabilities: tuple[str, ...] = (),
    dependencies: tuple[str, ...] = (),
    resources: tuple[ResourceLimit, ...] = (),
    permissions: tuple[str, ...] = (),
    lifecycle: ExtensionLifecycleState = ExtensionLifecycleState.DISCOVERED,
    metadata: dict[str, str] | None = None,
) -> ExtensionContract:
    """Constrói um contrato de extensão de teste."""
    return ExtensionContract(
        id=identifier,
        name=name,
        description="Extensão utilitária de teste.",
        kind=kind,
        version=version,
        contract_version=contract_version,
        capabilities=capabilities,
        dependencies=dependencies,
        resources=resources,
        permissions=permissions,
        lifecycle=lifecycle,
        metadata=metadata or {},
    )


def test_contrato_valido_com_todos_os_campos() -> None:
    """Um contrato completo deve construir sem erros e preservar os valores."""
    limite = ResourceLimit(name="memory_mb", value=512.0)
    contrato = _contracto(
        identifier="wsai.agent.chat",
        name="Agente Chat",
        kind=ExtensionKind.AGENT,
        version="2.1.0",
        contract_version="1.0",
        capabilities=("local_llm_inference",),
        dependencies=("wsai.core",),
        resources=(limite,),
        permissions=("network:local",),
        lifecycle=ExtensionLifecycleState.READY,
        metadata={"autor": "teste"},
    )

    assert contrato.id == "wsai.agent.chat"
    assert contrato.name == "Agente Chat"
    assert contrato.kind is ExtensionKind.AGENT
    assert contrato.version == "2.1.0"
    assert contrato.contract_version == "1.0"
    assert contrato.capabilities == ("local_llm_inference",)
    assert contrato.dependencies == ("wsai.core",)
    assert contrato.resources == (limite,)
    assert contrato.permissions == ("network:local",)
    assert contrato.lifecycle is ExtensionLifecycleState.READY
    assert contrato.metadata == {"autor": "teste"}


def test_contrato_defaults_aplicados() -> None:
    """Os campos opcionais devem ter os valores predefinidos documentados."""
    contrato = _contracto()

    assert contrato.capabilities == ()
    assert contrato.dependencies == ()
    assert contrato.resources == ()
    assert contrato.permissions == ()
    assert contrato.lifecycle is ExtensionLifecycleState.DISCOVERED
    assert contrato.metadata == {}


def test_contrato_immutavel() -> None:
    """Um contrato validado não deve ser modificável (frozen)."""
    contrato = _contracto()
    with pytest.raises(Exception):
        contrato.name = "Nome alterado"  # type: ignore[misc]


def test_contrato_rejeita_id_vazio() -> None:
    """Um id vazio deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _contracto(identifier="")


def test_contrato_rejeita_nome_vazio() -> None:
    """Um nome vazio deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _contracto(name="")


def test_contrato_rejeita_versao_vazia() -> None:
    """Uma versão vazia deve ser rejeitada à criação."""
    with pytest.raises(ValueError):
        _contracto(version="")


def test_contrato_rejeita_versao_de_contrato_vazia() -> None:
    """Uma versão de contrato vazia deve ser rejeitada à criação."""
    with pytest.raises(ValueError):
        _contracto(contract_version="")


def test_contrato_rejeita_tipo_ausente() -> None:
    """Um tipo (kind) ausente ou nulo deve ser rejeitado à criação."""
    with pytest.raises(ValueError):
        _contracto(kind=None)  # type: ignore[arg-type]


def test_enum_tipos_cobre_categorias_conhecidas() -> None:
    """O tipo funcional deve cobrir as categorias previstas de addons."""
    valores = {kind.value for kind in ExtensionKind}
    assert {
        "analyst",
        "code",
        "agent",
        "github_tool",
        "mcp",
        "utility",
    } <= valores


def test_enum_lifecycle_segue_a_sequencia_prevista() -> None:
    """O lifecycle deve conter os estados da sequência do hardening 02."""
    sequencia = [estado.value for estado in ExtensionLifecycleState]
    assert "discovered" in sequencia
    assert "validated" in sequencia
    assert "registered" in sequencia
    assert "initializing" in sequencia
    assert "ready" in sequencia
    assert "running" in sequencia
    assert "degraded" in sequencia
    assert "failed" in sequencia
    assert "stopping" in sequencia
    assert "stopped" in sequencia


def test_limite_de_recurso_com_resumo() -> None:
    """Um limite de recurso deve expor um resumo textual."""
    limite = ResourceLimit(name="cpu", value=2.0)
    assert limite.summary == "cpu=2.0"


def test_contrato_resumo_textual() -> None:
    """O contrato deve expor um resumo textual com identidade, tipo e lifecycle."""
    contrato = _contracto(
        identifier="wsai.code",
        name="Executor de Código",
        kind=ExtensionKind.CODE,
        version="1.2.0",
        lifecycle=ExtensionLifecycleState.VALIDATED,
    )
    resumo = contrato.summary
    assert "Executor de Código" in resumo
    assert "1.2.0" in resumo
    assert "code" in resumo
    assert "validated" in resumo