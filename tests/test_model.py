"""Testes do subsistema Model Intelligence — registo, metadados e requisitos.

Valida o contrato declarativo de modelos (definições, metadados e
requisitos) e o registo central com o catálogo base.
"""

from wsai2.model import (
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRegistry,
    ModelRequirements,
    create_default_registry,
    default_models,
)


def test_catalogo_base_contem_tres_modelos() -> None:
    """O catálogo base deve ter três modelos declarativos."""
    models = default_models()

    assert len(models) == 3
    model_ids = {model.id for model in models}
    assert model_ids == {
        "qwen2.5-7b-instruct",
        "phi-3-mini",
        "all-MiniLM-L6-v2",
    }


def test_catalogo_modelos_tipos_validos() -> None:
    """Cada modelo deve ser uma definição com campos coerentes."""
    for model in default_models():
        assert isinstance(model, ModelDefinition)
        assert isinstance(model.name, str) and len(model.name) > 0
        assert isinstance(model.description, str) and len(model.description) > 0
        assert model.kind in ModelKind
        assert isinstance(model.metadata, ModelMetadata)
        assert model.metadata.params_billions > 0
        assert model.metadata.context_window_tokens > 0
        assert isinstance(model.requirements, ModelRequirements)


def test_kind_dos_modelos_catalogo() -> None:
    """Os tipos dos modelos do catálogo devem estar correctos."""
    por_id = {model.id: model for model in default_models()}

    assert por_id["qwen2.5-7b-instruct"].kind is ModelKind.LLM
    assert por_id["phi-3-mini"].kind is ModelKind.LLM
    assert por_id["all-MiniLM-L6-v2"].kind is ModelKind.EMBEDDING


def test_requisitos_capacidades_requeridas() -> None:
    """Os requisitos devem referir as capacidades do sistema necessárias."""
    por_id = {model.id: model for model in default_models()}

    assert por_id["qwen2.5-7b-instruct"].requirements.required_capabilities == (
        "local_llm_inference",
    )
    assert por_id["all-MiniLM-L6-v2"].requirements.required_capabilities == (
        "local_embeddings",
    )


def test_requisitos_gpu_apenas_quando_exigido() -> None:
    """has_gpu_requirement deve reflectir as exigências de GPU."""
    for model in default_models():
        req = model.requirements
        assert req.has_gpu_requirement == (req.requires_gpu or req.min_vram_gb is not None)

    assert default_models()[0].requirements.has_gpu_requirement is False


def test_registo_padrao_com_catalogo_base() -> None:
    """O registo padrão deve conter todo o catálogo base."""
    registry = create_default_registry()

    assert len(registry) == len(default_models())
    assert {model.id for model in registry.all()} == {
        model.id for model in default_models()
    }


def test_registo_obter_e_verificar() -> None:
    """get/has devem responder correctamente por id."""
    registry = create_default_registry()

    model = registry.get("phi-3-mini")
    assert model is not None
    assert model.id == "phi-3-mini"
    assert registry.has("phi-3-mini") is True
    assert registry.get("inexistente") is None
    assert registry.has("inexistente") is False


def test_registo_registrar_substitui() -> None:
    """Registar um id já existente deve substituí-lo."""
    registry = create_default_registry()
    original = registry.get("phi-3-mini")
    assert original is not None

    novo = ModelDefinition(
        id="phi-3-mini",
        name="Phi-3 Mini (nova versão)",
        description="Versão actualizada para testes.",
        kind=ModelKind.LLM,
        metadata=ModelMetadata(
            version="4",
            params_billions=4.0,
            context_window_tokens=8192,
        ),
        requirements=ModelRequirements(min_ram_gb=4.0, min_cpu_cores=2),
    )
    registry.register(novo)

    assert registry.get("phi-3-mini").name == "Phi-3 Mini (nova versão)"
    assert len(registry) == len(default_models())


def test_registo_remover() -> None:
    """unregister deve remover e devolver estado correcto."""
    registry = create_default_registry()

    assert registry.unregister("phi-3-mini") is True
    assert registry.has("phi-3-mini") is False
    assert len(registry) == len(default_models()) - 1
    assert registry.unregister("phi-3-mini") is False


def test_registo_vazio_init() -> None:
    """Um registo criado sem definições deve começar vazio."""
    registry = ModelRegistry()

    assert len(registry) == 0
    assert registry.all() == ()


def test_resumo_textual_do_modelo() -> None:
    """O resumo do modelo deve conter nome e id."""
    model = default_models()[0]

    assert model.name in model.summary
    assert model.id in model.summary