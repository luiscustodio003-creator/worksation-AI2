"""Testes do subsistema Model Intelligence — classificação e score.

Valida a atribuição de categoria funcional e do score de adequação
(0.0–1.0) derivado da compatibilidade, bem como a classificação de todo
o registo.
"""

from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.hardware import Architecture, CpuInfo, CpuVendor, GpuInfo, HardwareProfile, MemoryInfo, StorageInfo
from wsai2.model import (
    ModelCategory,
    ModelClassification,
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRequirements,
    adequacy_score,
    category_for,
    classify_model,
    classify_models,
    create_default_registry,
    default_models,
    evaluate_models,
)
from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile
from wsai2.model.base import ModelState

_GB = 1024 ** 3


def _hardware(
    ram_gb: float = 16.0,
    cores: int = 8,
    vram_gb: float | None = None,
    storage_gb: float = 500.0,
) -> HardwareProfile:
    """Constrói um HardwareProfile de teste."""
    gpus = ()
    if vram_gb:
        gpus = (
            GpuInfo(name="GPU Teste", vendor="nvidia", vram_bytes=int(vram_gb * _GB)),
        )
    return HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL,
            model_name="CPU de Teste",
            architecture=Architecture.X86_64,
            physical_cores=cores,
            logical_cores=cores * 2,
        ),
        memory=MemoryInfo(total_bytes=int(ram_gb * _GB)),
        gpus=gpus,
        storage=(
            StorageInfo(
                device_path="C:",
                total_bytes=int(storage_gb * _GB),
                type="ssd",
                mount_point="C:",
            ),
        ),
    )


def _runtime(ram_gb: float = 16.0, available_gb: float = 6.0) -> RuntimeProfile:
    """Constrói um RuntimeProfile de teste."""
    used = ram_gb - available_gb
    percent = (used / ram_gb) * 100.0 if ram_gb else 0.0
    return RuntimeProfile(
        cpu=CpuLoad(percent=30.0, per_core=(), count=8),
        memory=MemoryRuntime(
            total_bytes=int(ram_gb * _GB),
            available_bytes=int(available_gb * _GB),
            used_bytes=int(used * _GB),
            percent=percent,
        ),
    )


def test_categoria_declarada_no_catalogo() -> None:
    """As categorias do catálogo base devem estar correctas."""
    por_id = {model.id: model for model in default_models()}

    assert category_for(por_id["qwen2.5-7b-instruct"]) is ModelCategory.CHAT
    assert category_for(por_id["phi-3-mini"]) is ModelCategory.CHAT
    assert category_for(por_id["all-MiniLM-L6-v2"]) is ModelCategory.EMBEDDING


def test_categoria_derivada_do_tipo() -> None:
    """Sem categoria declarada, a categoria deve derivar do tipo."""
    modelo_llm = ModelDefinition(
        id="llm-sem-categoria",
        name="LLM",
        description="Modelo de teste.",
        kind=ModelKind.LLM,
        metadata=ModelMetadata(version="1", params_billions=1.0, context_window_tokens=1024),
    )
    modelo_emb = ModelDefinition(
        id="emb-sem-categoria",
        name="Embedding",
        description="Modelo de teste.",
        kind=ModelKind.EMBEDDING,
        metadata=ModelMetadata(version="1", params_billions=0.02, context_window_tokens=128),
    )

    assert category_for(modelo_llm) is ModelCategory.CHAT
    assert category_for(modelo_emb) is ModelCategory.EMBEDDING


def test_categoria_sobrepoe_a_derivacao() -> None:
    """A categoria declarada deve sobrepor-se à derivação por tipo."""
    modelo = ModelDefinition(
        id="completion-declarado",
        name="Completion",
        description="Modelo de teste.",
        kind=ModelKind.LLM,
        metadata=ModelMetadata(version="1", params_billions=1.0, context_window_tokens=1024),
        category=ModelCategory.COMPLETION,
    )

    assert category_for(modelo) is ModelCategory.COMPLETION


def test_score_adequacao_por_estado() -> None:
    """O score de adequação deve seguir a rubrica documentada."""
    modelos = create_default_registry()
    capabilities = create_capability_registry()

    # 6GB disponíveis → all-MiniLM disponível, LLMs condicionados
    veredictos = {
        v.model_id: v for v in evaluate_models(modelos, _hardware(), _runtime(), capabilities)
    }

    minim = veredictos["all-MiniLM-L6-v2"]
    qwen = veredictos["qwen2.5-7b-instruct"]

    assert minim.state is ModelState.AVAILABLE
    assert adequacy_score(minim) == 1.0
    assert qwen.state is ModelState.RESTRICTED
    assert adequacy_score(qwen) == 0.5


def test_score_indisponivel_zero() -> None:
    """Um modelo indisponível deve ter score 0.0."""
    modelo = ModelDefinition(
        id="gpu-obrigatoria",
        name="GPU",
        description="Modelo de teste.",
        kind=ModelKind.LLM,
        metadata=ModelMetadata(version="1", params_billions=1.0, context_window_tokens=1024),
        requirements=ModelRequirements(
            min_vram_gb=4.0,
            requires_gpu=True,
            required_capabilities=("accelerated_ml",),
        ),
    )

    classificacao = classify_model(
        modelo, _hardware(), _runtime(), create_capability_registry()
    )

    assert classificacao.score == 0.0
    assert classificacao.verdict.state is ModelState.UNAVAILABLE


def test_classificacao_modelo_disponivel() -> None:
    """Um modelo disponível deve classificar com score 1.0 e categoria certa."""
    modelos = create_default_registry()
    definition = modelos.get("all-MiniLM-L6-v2")
    assert definition is not None

    classificacao = classify_model(
        definition,
        _hardware(),
        _runtime(available_gb=16.0),
        create_capability_registry(),
    )

    assert isinstance(classificacao, ModelClassification)
    assert classificacao.category is ModelCategory.EMBEDDING
    assert classificacao.score == 1.0
    assert classificacao.is_available is True


def test_classificacao_com_runtime_folgado() -> None:
    """Com memória suficiente, todos os modelos base devem ter score 1.0."""
    modelos = create_default_registry()

    classificacoes = classify_models(
        modelos,
        _hardware(),
        _runtime(available_gb=16.0),
        create_capability_registry(),
    )

    assert len(classificacoes) == len(modelos)
    assert all(c.score == 1.0 for c in classificacoes)
    assert all(c.is_available for c in classificacoes)


def test_classificacao_reflecte_condicionamentos() -> None:
    """Com runtime condicionado, entre 0 e 1 existem scores 0.5."""
    modelos = create_default_registry()

    classificacoes = classify_models(
        modelos, _hardware(), _runtime(), create_capability_registry()
    )

    por_id = {c.model_id: c for c in classificacoes}
    assert por_id["all-MiniLM-L6-v2"].score == 1.0
    assert por_id["qwen2.5-7b-instruct"].score == 0.5
    assert por_id["phi-3-mini"].score == 0.5


def test_classificacao_cobre_todo_o_registo() -> None:
    """classify_models deve devolver uma classificação por modelo."""
    modelos = create_default_registry()

    classificacoes = classify_models(
        modelos, _hardware(), _runtime(), create_capability_registry()
    )

    ids = {c.model_id for c in classificacoes}
    assert ids == {model.id for model in default_models()}