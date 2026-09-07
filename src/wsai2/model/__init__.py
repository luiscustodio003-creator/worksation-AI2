"""Subsistema Model Intelligence do WorkStation AI 2.

Responsável por manter informação sobre os modelos conhecidos do
sistema: metadados, requisitos, compatibilidade, desempenho e
adequação às tarefas (subsistema 3.5 da arquitectura).

Nesta unidade inicial são implementados o **registo de modelos** e os
**metadados e requisitos** declarativos. A compatibilidade e a
recomendação fazem parte das unidades seguintes da Fase 5.
"""

from .base import ModelDefinition, ModelKind, ModelMetadata, ModelRequirements
from .registry import ModelRegistry, create_default_registry, default_models

__all__ = [
    "ModelDefinition",
    "ModelKind",
    "ModelMetadata",
    "ModelRegistry",
    "ModelRequirements",
    "create_default_registry",
    "default_models",
]