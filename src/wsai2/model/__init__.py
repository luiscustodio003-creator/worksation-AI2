"""Subsistema Model Intelligence do WorkStation AI 2.

Responsável por manter informação sobre os modelos conhecidos do
sistema: metadados, requisitos, compatibilidade, desempenho e
adequação às tarefas (subsistema 3.5 da arquitectura).

Nesta unidade foi adicionada a **recomendação de modelos**: selecção do
modelo mais adequado por categoria e score de adequação, com
justificação e alternativas. Com esta unidade, a Fase 5 fica **concluída**
(registo, metadados, requisitos, compatibilidade, classificação e
recomendação).
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
from .recommendation import ModelRecommendation, recommend_model
from .registry import ModelRegistry, create_default_registry, default_models

__all__ = [
    "ModelCategory",
    "ModelCheck",
    "ModelClassification",
    "ModelDefinition",
    "ModelKind",
    "ModelMetadata",
    "ModelRecommendation",
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
    "recommend_model",
]