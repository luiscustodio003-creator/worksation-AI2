"""Subsistema Model Intelligence do WorkStation AI 2.

Responsável por manter informação sobre os modelos conhecidos do
sistema: metadados, requisitos, compatibilidade, desempenho e
adequação às tarefas (subsistema 3.5 da arquitectura).

Nesta unidade foi adicionada a **classificação dos modelos**: categoria
funcional primária (chat/completion/embedding) e score de adequação
(0.0–1.0) derivado da compatibilidade. A recomendação — que combina
categoria, score e critérios da tarefa — é a unidade que encerra a
Fase 5.
"""

from .base import (
    ModelCategory,
    ModelCheck,
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRequirements,
    ModelState,
    ModelVerdict,
)
from .classification import (
    ModelClassification,
    adequacy_score,
    category_for,
    classify_model,
    classify_models,
)
from .compatibility import compatible_models, evaluate_model, evaluate_models
from .registry import ModelRegistry, create_default_registry, default_models

__all__ = [
    "ModelCategory",
    "ModelCheck",
    "ModelClassification",
    "ModelDefinition",
    "ModelKind",
    "ModelMetadata",
    "ModelRegistry",
    "ModelRequirements",
    "ModelState",
    "ModelVerdict",
    "adequacy_score",
    "category_for",
    "classify_model",
    "classify_models",
    "compatible_models",
    "create_default_registry",
    "default_models",
    "evaluate_model",
    "evaluate_models",
]