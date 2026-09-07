"""Testes do subsistema Provider Layer — contratos e registo.

Valida o contrato declarativo de fornecedores (definições e tipos) e o
registo central com o catálogo base.
"""

from wsai2.provider import (
    ProviderDefinition,
    ProviderRegistry,
    ProviderType,
    create_default_registry,
    default_providers,
)


def test_catalogo_base_contem_tres_fornecedores() -> None:
    """O catálogo base deve ter três fornecedores declarativos."""
    providers = default_providers()

    assert len(providers) == 3
    provider_ids = {provider.id for provider in providers}
    assert provider_ids == {"ollama", "llama_cpp", "openai_compatible"}


def test_fornecedores_tipos_validos() -> None:
    """Cada fornecedor deve ser uma definição com campos coerentes."""
    for provider in default_providers():
        assert isinstance(provider, ProviderDefinition)
        assert isinstance(provider.name, str) and len(provider.name) > 0
        assert isinstance(provider.description, str) and len(provider.description) > 0
        assert provider.type in ProviderType
        assert isinstance(provider.default_base_url, str)


def test_tipos_dos_fornecedores_catalogo() -> None:
    """Os tipos dos fornecedores do catálogo devem estar correctos."""
    por_id = {provider.id: provider for provider in default_providers()}

    assert por_id["ollama"].type is ProviderType.LOCAL_RUNTIME
    assert por_id["llama_cpp"].type is ProviderType.LOCAL_RUNTIME
    assert por_id["openai_compatible"].type is ProviderType.REMOTE_API


def test_capacidades_fornecidas() -> None:
    """Os fornecedores locais devem declarar as capacidades que disponibilizam."""
    por_id = {provider.id: provider for provider in default_providers()}

    assert por_id["ollama"].capabilities_provided == (
        "local_llm_inference",
        "local_embeddings",
    )
    assert por_id["llama_cpp"].capabilities_provided == ("local_llm_inference",)
    assert por_id["openai_compatible"].capabilities_provided == ()


def test_uris_base_predefinidas() -> None:
    """As URIs base predefinidas devem estar presentes."""
    por_id = {provider.id: provider for provider in default_providers()}

    assert por_id["ollama"].default_base_url.startswith("http")
    assert por_id["llama_cpp"].default_base_url.startswith("http")
    assert por_id["openai_compatible"].default_base_url.startswith("https")


def test_registo_padrao_com_catalogo_base() -> None:
    """O registo padrão deve conter todo o catálogo base."""
    registry = create_default_registry()

    assert len(registry) == len(default_providers())
    assert {provider.id for provider in registry.all()} == {
        provider.id for provider in default_providers()
    }


def test_registo_obter_e_verificar() -> None:
    """get/has devem responder correctamente por id."""
    registry = create_default_registry()

    provider = registry.get("ollama")
    assert provider is not None
    assert provider.id == "ollama"
    assert registry.has("ollama") is True
    assert registry.get("inexistente") is None
    assert registry.has("inexistente") is False


def test_registo_registrar_substitui() -> None:
    """Registar um id já existente deve substituí-lo."""
    registry = create_default_registry()
    original = registry.get("ollama")
    assert original is not None

    novo = ProviderDefinition(
        id="ollama",
        name="Ollama (nova versão)",
        description="Versão actualizada para testes.",
        type=ProviderType.LOCAL_RUNTIME,
        default_base_url="http://localhost:11435",
    )
    registry.register(novo)

    assert registry.get("ollama").name == "Ollama (nova versão)"
    assert len(registry) == len(default_providers())


def test_registo_remover() -> None:
    """unregister deve remover e devolver estado correcto."""
    registry = create_default_registry()

    assert registry.unregister("llama_cpp") is True
    assert registry.has("llama_cpp") is False
    assert len(registry) == len(default_providers()) - 1
    assert registry.unregister("llama_cpp") is False


def test_registo_vazio_init() -> None:
    """Um registo criado sem definições deve começar vazio."""
    registry = ProviderRegistry()

    assert len(registry) == 0
    assert registry.all() == ()


def test_resumo_textual_do_fornecedor() -> None:
    """O resumo do fornecedor deve conter nome e id."""
    provider = default_providers()[0]

    assert provider.name in provider.summary
    assert provider.id in provider.summary