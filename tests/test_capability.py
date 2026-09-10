"""Testes do subsistema Capability Engine — definições e registo.

Valida os contratos de definição de capacidade, os requisitos
quantificados e o comportamento do registo central.
"""

from wsai2.capability import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRequirements,
    create_default_registry,
    default_capabilities,
)
from wsai2.hardware import CapabilityDomain


def test_capability_requirements_padrao() -> None:
    """Os requisitos por defeito devem ser usáveis e coerentes."""
    req = CapabilityRequirements()

    assert req.min_ram_gb == 1.0
    assert req.min_cpu_cores == 1
    assert req.requires_gpu is False
    assert req.min_vram_gb is None
    assert req.min_available_disk_gb == 0.0
    assert req.has_gpu_requirement is False


def test_capability_requirements_gpu() -> None:
    """Requisitos com GPU obrigatória devem sinalizá-la."""
    req = CapabilityRequirements(min_vram_gb=4.0, requires_gpu=True)

    assert req.has_gpu_requirement is True
    assert req.min_vram_gb == 4.0
    assert req.min_ram_gb == 1.0  # valor por defeito mantém-se


def test_capability_definition_estrutura() -> None:
    """Uma definição de capacidade deve ter campos obrigatórios."""
    definition = CapabilityDefinition(
        id="exemplo",
        name="Capacidade exemplo",
        description="Descrição de exemplo.",
        requirements=CapabilityRequirements(min_ram_gb=2.0),
    )

    assert definition.id == "exemplo"
    assert definition.name == "Capacidade exemplo"
    assert definition.description == "Descrição de exemplo."
    assert definition.requirements.min_ram_gb == 2.0
    assert isinstance(definition.summary, str)
    assert len(definition.summary) > 0
    assert "exemplo" in definition.summary


def test_capacidades_default_nao_vazias() -> None:
    """O catálogo base deve conter pelo menos uma capacidade."""
    capabilities = default_capabilities()

    assert isinstance(capabilities, tuple)
    assert len(capabilities) > 0
    for capability in capabilities:
        assert isinstance(capability, CapabilityDefinition)
        assert isinstance(capability.id, str)
        assert len(capability.id) > 0
        assert isinstance(capability.name, str)
        assert len(capability.name) > 0


def test_capacidades_default_ids_unicos() -> None:
    """Os ids do catálogo base devem ser únicos."""
    capabilities = default_capabilities()
    ids = [capability.id for capability in capabilities]
    assert len(ids) == len(set(ids))


def test_capacidades_default_dominios() -> None:
    """O catálogo base associa cada capacidade a um domínio."""
    capabilities = default_capabilities()
    dominios = {capability.domain for capability in capabilities}
    assert CapabilityDomain.COMPUTE in dominios
    assert CapabilityDomain.GRAPHICS in dominios
    acelerado = next(c for c in capabilities if c.id == "accelerated_ml")
    assert acelerado.domain is CapabilityDomain.GRAPHICS


def test_definicao_dominio_padrao() -> None:
    """Uma definição simples pertence por defeito ao domínio COMPUTE."""
    definition = CapabilityDefinition(id="teste", name="Teste", description="Def. de teste.")
    assert definition.domain is CapabilityDomain.COMPUTE


def test_registo_registar_e_obter() -> None:
    """O registo deve guardar e devolver definições por id."""
    registry = CapabilityRegistry()
    definition = CapabilityDefinition(id="teste", name="Teste", description="Def. de teste.")

    registry.register(definition)

    assert registry.has("teste") is True
    assert registry.get("teste") == definition
    assert registry.get("inexistente") is None


def test_registo_substituir_mesmo_id() -> None:
    """Registar o mesmo id deve substituir a definição anterior."""
    registry = CapabilityRegistry()
    primeira = CapabilityDefinition(id="teste", name="Primeira", description="Def. de teste.")
    segunda = CapabilityDefinition(id="teste", name="Segunda", description="Def. de teste.")

    registry.register(primeira)
    registry.register(segunda)

    assert registry.get("teste") == segunda
    assert registry.get("teste").name == "Segunda"


def test_registo_remover() -> None:
    """O registo deve remover definições e devolver indicação de sucesso."""
    registry = CapabilityRegistry()
    definition = CapabilityDefinition(id="teste", name="Teste", description="Def. de teste.")
    registry.register(definition)

    assert registry.unregister("teste") is True
    assert registry.has("teste") is False
    assert registry.unregister("teste") is False


def test_registo_lista_todas() -> None:
    """O registo deve listar todas as definições com número coerente."""
    registry = create_default_registry()

    all_defs = registry.all()
    assert len(all_defs) == len(registry)
    assert len(all_defs) == len(default_capabilities())


def test_registo_default_precarregado() -> None:
    """O registo por defeito deve conter o catálogo base."""
    registry = create_default_registry()

    for capability in default_capabilities():
        assert registry.has(capability.id)


def test_registo_vazio_inicia_sem_definicoes() -> None:
    """Um registo sem argumentos não deve conter definições."""
    registry = CapabilityRegistry()

    assert len(registry) == 0
    assert registry.all() == ()