"""Classificação dos modelos e score de adequação.

Atribui a cada modelo conhecido uma **categoria funcional** primária
(chat, completion, embedding) e um **score de adequação** (0.0–1.0)
derivado do veredicto de compatibilidade, determinando, de forma
determinística e documentada, a prontidão do modelo para ser usado no
sistema.

Rubrica do score de adequação:

- ``1.0`` — modelo **disponível** (AVAILABLE): requisitos do modelo e
  capacidades requeridas totalmente satisfeitos;
- ``0.5`` — modelo **condicionado** (RESTRICTED): executável, mas com
  capacidades ou recursos momentâneos insuficientes;
- ``0.0`` — modelo **indisponível** (UNAVAILABLE): requisitos mínimos
  ou capacidades requeridas não satisfeitos.

Esta rubrica simples é a base; a unidade de **recomendação** da Fase 5
combina a categoria e o score com critérios da tarefa a executar.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import (
    ModelCategory,
    ModelDefinition,
    ModelKind,
    ModelState,
    ModelVerdict,
)
from .compatibility import evaluate_model, evaluate_models
from .registry import ModelRegistry
from wsai2.capability import CapabilityRegistry
from wsai2.hardware import HardwareProfile
from wsai2.runtime import RuntimeProfile


@dataclass(frozen=True)
class ModelClassification:
    """Classificação de um modelo: categoria, score e veredicto.

    Reúne a categoria funcional primária, o score de adequação derivado
    da compatibilidade e o próprio veredicto que o justifica.
    """

    model_id: str
    category: ModelCategory
    score: float
    verdict: ModelVerdict

    @property
    def is_available(self) -> bool:
        """Indica se o modelo está disponível para uso."""
        return self.verdict.is_available


def category_for(definition: ModelDefinition) -> ModelCategory:
    """Devolve a categoria funcional primária de um modelo.

    Usa a categoria declarada na definição ou, na sua ausência, deriva
    uma categoria do tipo do modelo (LLM → chat; embedding → embedding).
    """
    if definition.category is not None:
        return definition.category
    if definition.kind is ModelKind.EMBEDDING:
        return ModelCategory.EMBEDDING
    return ModelCategory.CHAT


def adequacy_score(verdict: ModelVerdict) -> float:
    """Score de adequação (0.0–1.0) derivado do veredicto.

    Rubrica documentada no módulo: disponível = 1.0, condicionado = 0.5,
    indisponível = 0.0.
    """
    if verdict.state is ModelState.AVAILABLE:
        return 1.0
    if verdict.state is ModelState.RESTRICTED:
        return 0.5
    return 0.0


def classify_model(
    definition: ModelDefinition,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
) -> ModelClassification:
    """Classifica um modelo: categoria, veredicto e score de adequação."""
    verdict = evaluate_model(definition, hardware, runtime, capability_registry)
    return ModelClassification(
        model_id=definition.id,
        category=category_for(definition),
        score=adequacy_score(verdict),
        verdict=verdict,
    )


def classify_models(
    model_registry: ModelRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
) -> tuple[ModelClassification, ...]:
    """Classifica todos os modelos registados contra o sistema."""
    return tuple(
        ModelClassification(
            model_id=verdict.model_id,
            category=category_for(definition),
            score=adequacy_score(verdict),
            verdict=verdict,
        )
        for definition, verdict in zip(
            model_registry.all(),
            evaluate_models(model_registry, hardware, runtime, capability_registry),
        )
    )


__all__ = [
    "ModelClassification",
    "adequacy_score",
    "category_for",
    "classify_model",
    "classify_models",
]