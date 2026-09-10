"""Registo de definições de capacidade.

Este módulo mantém o catálogo de capacidades conhecidas do sistema e
fornece a implementação concreta do registo central usado pelas
unidades seguintes da Fase 4 (avaliação, compatibilidade,
capacidades disponíveis).
"""

from __future__ import annotations

from wsai2.hardware import CapabilityDomain

from .base import CapabilityDefinition, CapabilityRequirements

# Catálogo base de capacidades fundamentais do WorkStation AI 2.
# Entradas puramente declarativas (dados, sem lógica) — servem de base
# à avaliação de disponibilidade nas unidades seguintes da Fase 4.
# Cada definição identifica o domínio de capacidade a que pertence
# (CapabilityDomain, de wsai2.hardware).
_DEFAULT_CAPABILITY_DEFINITIONS: tuple[CapabilityDefinition, ...] = (
    CapabilityDefinition(
        id="local_llm_inference",
        name="Inferência local de LLM",
        description=(
            "Execução de inferência de modelos de linguagem grandes "
            "localmente no sistema."
        ),
        requirements=CapabilityRequirements(
            min_ram_gb=8.0,
            min_cpu_cores=4,
        ),
        domain=CapabilityDomain.COMPUTE,
    ),
    CapabilityDefinition(
        id="local_embeddings",
        name="Embeddings locais",
        description=(
            "Geração de representações vectoriais com modelos locais."
        ),
        requirements=CapabilityRequirements(
            min_ram_gb=4.0,
            min_cpu_cores=2,
        ),
        domain=CapabilityDomain.COMPUTE,
    ),
    CapabilityDefinition(
        id="accelerated_ml",
        name="ML acelerado por GPU",
        description=(
            "Execução acelerada de workloads de aprendizagem automática."
        ),
        requirements=CapabilityRequirements(
            min_ram_gb=8.0,
            min_vram_gb=4.0,
            requires_gpu=True,
            min_cpu_cores=4,
        ),
        domain=CapabilityDomain.GRAPHICS,
    ),
    CapabilityDefinition(
        id="lightweight_processing",
        name="Processamento de texto leve",
        description=(
            "Operações de processamento de texto sem modelos pesados."
        ),
        requirements=CapabilityRequirements(
            min_ram_gb=1.0,
            min_cpu_cores=1,
        ),
        domain=CapabilityDomain.COMPUTE,
    ),
)


def default_capabilities() -> tuple[CapabilityDefinition, ...]:
    """Devolve o catálogo base de definições de capacidade."""
    return _DEFAULT_CAPABILITY_DEFINITIONS


class CapabilityRegistry:
    """Registo central das definições de capacidade conhecidas.

    Responsabilidade única: manter e consultar o catálogo de definições
    de capacidade disponíveis para avaliação. Não executa avaliação —
    essa responsabilidade pertence a módulos dedicados das unidades
    seguintes.
    """

    def __init__(self, definitions: tuple[CapabilityDefinition, ...] = ()) -> None:
        self._definitions: dict[str, CapabilityDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: CapabilityDefinition) -> None:
        """Regista uma definição de capacidade.

        Se já existir uma definição com o mesmo id, substitui-a.
        """
        self._definitions[definition.id] = definition

    def unregister(self, capability_id: str) -> bool:
        """Remove uma definição de capacidade.

        Devolve ``True`` se a capacidade existia e foi removida.
        """
        return self._definitions.pop(capability_id, None) is not None

    def get(self, capability_id: str) -> CapabilityDefinition | None:
        """Obtém uma definição de capacidade pelo id.

        Devolve ``None`` quando o id não está registado.
        """
        return self._definitions.get(capability_id)

    def has(self, capability_id: str) -> bool:
        """Indica se uma capacidade está registada."""
        return capability_id in self._definitions

    def all(self) -> tuple[CapabilityDefinition, ...]:
        """Devolve todas as definições registadas."""
        return tuple(self._definitions.values())

    def __len__(self) -> int:
        """Número de definições registadas."""
        return len(self._definitions)


def create_default_registry() -> CapabilityRegistry:
    """Cria um registo pré-carregado com o catálogo base."""
    return CapabilityRegistry(default_capabilities())


__all__ = ["CapabilityRegistry", "create_default_registry", "default_capabilities"]