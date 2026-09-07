"""Registo de definições de modelo.

Este módulo mantém o catálogo de modelos conhecidos do sistema e
fornece a implementação concreta do registo central usado pelas
unidades seguintes da Fase 5 (compatibilidade, classificação,
recomendação).
"""

from __future__ import annotations

from .base import (
    ModelCategory,
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRequirements,
)

# Catálogo base de modelos suportados pelo WorkStation AI 2.
# Entradas puramente declarativas (dados, sem lógica) — servem de base
# à avaliação de compatibilidade nas unidades seguintes da Fase 5.
_DEFAULT_MODEL_DEFINITIONS: tuple[ModelDefinition, ...] = (
    ModelDefinition(
        id="qwen2.5-7b-instruct",
        name="Qwen 2.5 7B Instruct",
        description=(
            "Modelo de linguagem para chat e instruções, executado "
            "localmente no sistema."
        ),
        kind=ModelKind.LLM,
        metadata=ModelMetadata(
            version="2.5",
            params_billions=7.6,
            context_window_tokens=32768,
            license="Apache 2.0",
            architecture="transformer",
        ),
        category=ModelCategory.CHAT,
        requirements=ModelRequirements(
            min_ram_gb=8.0,
            min_cpu_cores=4,
            min_available_disk_gb=16.0,
            required_capabilities=("local_llm_inference",),
        ),
    ),
    ModelDefinition(
        id="phi-3-mini",
        name="Phi-3 Mini",
        description=(
            "Modelo de linguagem compacto para chat e instruções, "
            "adequado a sistemas com menos recursos."
        ),
        kind=ModelKind.LLM,
        metadata=ModelMetadata(
            version="3",
            params_billions=3.8,
            context_window_tokens=4096,
            license="MIT",
            architecture="transformer",
        ),
        category=ModelCategory.CHAT,
        requirements=ModelRequirements(
            min_ram_gb=4.0,
            min_cpu_cores=2,
            min_available_disk_gb=8.0,
            required_capabilities=("local_llm_inference",),
        ),
    ),
    ModelDefinition(
        id="all-MiniLM-L6-v2",
        name="All MiniLM L6 v2",
        description=(
            "Modelo de embeddings para geração de representações "
            "vectoriais com mínimo de recursos."
        ),
        kind=ModelKind.EMBEDDING,
        metadata=ModelMetadata(
            version="v2",
            params_billions=0.0227,
            context_window_tokens=256,
            license="Apache 2.0",
            architecture="transformer",
        ),
        category=ModelCategory.EMBEDDING,
        requirements=ModelRequirements(
            min_ram_gb=1.0,
            min_cpu_cores=1,
            min_available_disk_gb=1.0,
            required_capabilities=("local_embeddings",),
        ),
    ),
)


def default_models() -> tuple[ModelDefinition, ...]:
    """Devolve o catálogo base de definições de modelo."""
    return _DEFAULT_MODEL_DEFINITIONS


class ModelRegistry:
    """Registo central das definições de modelo conhecidas.

    Responsabilidade única: manter e consultar o catálogo de modelos
    disponíveis para compatibilidade. Não executa avaliação — essa
    responsabilidade pertence a módulos dedicados das unidades
    seguintes.
    """

    def __init__(self, definitions: tuple[ModelDefinition, ...] = ()) -> None:
        self._definitions: dict[str, ModelDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: ModelDefinition) -> None:
        """Regista uma definição de modelo.

        Se já existir um modelo com o mesmo id, substitui-o.
        """
        self._definitions[definition.id] = definition

    def unregister(self, model_id: str) -> bool:
        """Remove uma definição de modelo.

        Devolve ``True`` se o modelo existia e foi removido.
        """
        return self._definitions.pop(model_id, None) is not None

    def get(self, model_id: str) -> ModelDefinition | None:
        """Obtém uma definição de modelo pelo id.

        Devolve ``None`` quando o id não está registado.
        """
        return self._definitions.get(model_id)

    def has(self, model_id: str) -> bool:
        """Indica se um modelo está registado."""
        return model_id in self._definitions

    def all(self) -> tuple[ModelDefinition, ...]:
        """Devolve todas as definições registadas."""
        return tuple(self._definitions.values())

    def __len__(self) -> int:
        """Número de definições registadas."""
        return len(self._definitions)


def create_default_registry() -> ModelRegistry:
    """Cria um registo pré-carregado com o catálogo base."""
    return ModelRegistry(default_models())


__all__ = ["ModelRegistry", "create_default_registry", "default_models"]