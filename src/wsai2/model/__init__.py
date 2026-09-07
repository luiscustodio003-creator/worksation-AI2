"""Subsistema Model Intelligence do WorkStation AI 2.

Responsável por manter informação sobre os modelos conhecidos do
sistema: metadados, requisitos, compatibilidade, desempenho e
adequação às tarefas (subsistema 3.5 da arquitectura).

Nesta unidade foi adicionada a **compatibilidade dos modelos**: avalia
cada modelo do registo contra o hardware, o runtime e as capacidades
requeridas do Capability Engine (veredictos disponível / condicionado /
indisponível com verificações por requisito). A classificação e a
recomendação fazem parte das unidades seguintes da Fase 5.
"""

from .base import (
    ModelCheck,
    ModelDefinition,
    ModelKind,
    ModelMetadata,
    ModelRequirements,
    ModelState,
    ModelVerdict,
)
from .compatibility import compatible_models, evaluate_model, evaluate_models
from .registry import ModelRegistry, create_default_registry, default_models

__all__ = [
    "ModelCheck",
    "ModelDefinition",
    "ModelKind",
    "ModelMetadata",
    "ModelRegistry",
    "ModelRequirements",
    "ModelState",
    "ModelVerdict",
    "compatible_models",
    "create_default_registry",
    "default_models",
    "evaluate_model",
    "evaluate_models",
]