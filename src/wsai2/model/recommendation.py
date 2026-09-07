"""Recomendação de modelos para uma tarefa ou critérios.

Dado o estado real do sistema (hardware, runtime e capacidades) e,
opcionalmente, uma categoria funcional pretendida, recomenda o modelo
**mais adequado** do registo, com justificação e alternativas.

Política de recomendação (determinística e documentada):

1. **Candidatos** — modelos com score de adequação > 0 (disponíveis ou
   condicionados) que correspondam à categoria pedida (ou todos, quando
   nenhuma categoria é indicada). Modelos indisponíveis (score 0.0)
   nunca são recomendados.
2. **Ordenação** — score de adequação decrescente; em caso de empate,
   modelo com mais parâmetros (mais capaz); depois menor exigência de
   RAM; e, por fim, id para estabilidade.
3. **Resultado** — o melhor candidato, com justificação textual,
   estado, categoria e as alternativas ordenadas (no máximo três).

Se não existirem candidatos, devolve ``None``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import (
    ModelCategory,
    ModelDefinition,
    ModelState,
    ModelVerdict,
)
from .classification import adequacy_score, category_for
from .compatibility import evaluate_models
from .registry import ModelRegistry
from wsai2.capability import CapabilityRegistry
from wsai2.hardware import HardwareProfile
from wsai2.runtime import RuntimeProfile

_NUM_ALTERNATIVAS = 3

_CATEGORY_LABELS = {
    ModelCategory.CHAT: "chat",
    ModelCategory.COMPLETION: "completion",
    ModelCategory.EMBEDDING: "embeddings",
}


@dataclass(frozen=True)
class ModelRecommendation:
    """Recomendação de um modelo para os critérios pedidos.

    Apresenta o modelo recomendado, o seu score de adequação, o estado
    de compatibilidade, uma justificação textual e as alternativas
    ordenadas (ids).
    """

    model_id: str
    name: str
    category: ModelCategory
    score: float
    state: ModelState
    reason: str
    alternatives: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_suitable(self) -> bool:
        """Indica se o modelo recomendado está de facto disponível."""
        return self.score == 1.0

    @property
    def summary(self) -> str:
        """Resumo textual da recomendação para apresentação."""
        return f"{self.name}: {self.reason}"


def _ranking_key(par: tuple[ModelDefinition, ModelVerdict]) -> tuple:
    """Chave de ordenação da política de recomendação."""
    definition, verdict = par
    return (
        -adequacy_score(verdict),
        -definition.metadata.params_billions,
        definition.requirements.min_ram_gb,
        definition.id,
    )


def recommend_model(
    model_registry: ModelRegistry,
    hardware: HardwareProfile,
    runtime: RuntimeProfile,
    capability_registry: CapabilityRegistry,
    category: ModelCategory | None = None,
) -> ModelRecommendation | None:
    """Recomenda o modelo mais adequado para os critérios indicados.

    Filtra por categoria quando indicada, exclui modelos
    indisponíveis e ordena conforme a política documentada no módulo.
    Devolve ``None`` quando não existe nenhum candidato.
    """
    pairs = list(
        zip(
            model_registry.all(),
            evaluate_models(model_registry, hardware, runtime, capability_registry),
        )
    )
    candidatos = [
        (definition, verdict)
        for definition, verdict in pairs
        if adequacy_score(verdict) > 0.0
        and (category is None or category_for(definition) is category)
    ]
    if not candidatos:
        return None

    candidatos.sort(key=_ranking_key)
    melhor_definition, melhor_verdict = candidatos[0]
    melhor_categoria = category_for(melhor_definition)
    score = adequacy_score(melhor_verdict)
    alternativas = tuple(
        definition.id for definition, _ in candidatos[1 : 1 + _NUM_ALTERNATIVAS]
    )

    label = _CATEGORY_LABELS.get(melhor_categoria, melhor_categoria.value)
    if score == 1.0:
        reason = f"Modelo disponível e mais adequado para {label}."
    else:
        reason = (
            f"Modelo mais adequado para {label}, mas condicionado "
            "no momento (capacidades ou recursos insuficientes)."
        )

    return ModelRecommendation(
        model_id=melhor_definition.id,
        name=melhor_definition.name,
        category=melhor_categoria,
        score=score,
        state=melhor_verdict.state,
        reason=reason,
        alternatives=alternativas,
    )


__all__ = ["ModelRecommendation", "recommend_model"]