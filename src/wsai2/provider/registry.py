"""Registo de definições de fornecedor.

Este módulo mantém o catálogo de fornecedores conhecidos do sistema e
fornece a implementação concreta do registo central usado pelas
unidades seguintes da Fase 6 (detecção, adaptadores, health checks).
"""

from __future__ import annotations

from .base import ProviderDefinition, ProviderType

# Catálogo base de fornecedores do WorkStation AI 2.
# Entradas puramente declarativas (dados, sem lógica) — servem de base
# à detecção e aos health checks nas unidades seguintes da Fase 6.
_DEFAULT_PROVIDER_DEFINITIONS: tuple[ProviderDefinition, ...] = (
    ProviderDefinition(
        id="ollama",
        name="Ollama",
        description=(
            "Runtime local que executa modelos de linguagem e "
            "embeddings no sistema."
        ),
        type=ProviderType.LOCAL_RUNTIME,
        default_base_url="http://localhost:11434",
        capabilities_provided=("local_llm_inference", "local_embeddings"),
    ),
    ProviderDefinition(
        id="llama_cpp",
        name="llama.cpp",
        description=(
            "Runtime local de inferência de LLM via llama.cpp, "
            "com servidor HTTP nativo."
        ),
        type=ProviderType.LOCAL_RUNTIME,
        default_base_url="http://localhost:8080",
        capabilities_provided=("local_llm_inference",),
    ),
    ProviderDefinition(
        id="openai_compatible",
        name="API compatível com OpenAI",
        description=(
            "API remota compatível com o contrato OpenAI (uri de "
            "base configurável)."
        ),
        type=ProviderType.REMOTE_API,
        default_base_url="https://api.openai.com/v1",
        capabilities_provided=(),
    ),
)


def default_providers() -> tuple[ProviderDefinition, ...]:
    """Devolve o catálogo base de definições de fornecedor."""
    return _DEFAULT_PROVIDER_DEFINITIONS


class ProviderRegistry:
    """Registo central das definições de fornecedor conhecidas.

    Responsabilidade única: manter e consultar o catálogo de
    fornecedores disponíveis para detecção e health checks. Não executa
    detecção — essa responsabilidade pertence a módulos dedicados das
    unidades seguintes.
    """

    def __init__(self, definitions: tuple[ProviderDefinition, ...] = ()) -> None:
        self._definitions: dict[str, ProviderDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: ProviderDefinition) -> None:
        """Regista uma definição de fornecedor.

        Se já existir um fornecedor com o mesmo id, substitui-o.
        """
        self._definitions[definition.id] = definition

    def unregister(self, provider_id: str) -> bool:
        """Remove uma definição de fornecedor.

        Devolve ``True`` se o fornecedor existia e foi removido.
        """
        return self._definitions.pop(provider_id, None) is not None

    def get(self, provider_id: str) -> ProviderDefinition | None:
        """Obtém uma definição de fornecedor pelo id.

        Devolve ``None`` quando o id não está registado.
        """
        return self._definitions.get(provider_id)

    def has(self, provider_id: str) -> bool:
        """Indica se um fornecedor está registado."""
        return provider_id in self._definitions

    def all(self) -> tuple[ProviderDefinition, ...]:
        """Devolve todas as definições registadas."""
        return tuple(self._definitions.values())

    def __len__(self) -> int:
        """Número de definições registadas."""
        return len(self._definitions)


def create_default_registry() -> ProviderRegistry:
    """Cria um registo pré-carregado com o catálogo base."""
    return ProviderRegistry(default_providers())


__all__ = ["ProviderRegistry", "create_default_registry", "default_providers"]