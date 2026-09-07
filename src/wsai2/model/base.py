"""Contratos e tipos fundamentais do Model Intelligence.

Este módulo contém apenas definições de tipos e dataclasses — não
implementa lógica de compatibilidade ou recomendação. Define o que é um
modelo conhecido pelo sistema e os seus requisitos mínimos para
execução local.

O *modelo* é a entidade central do subsistema 3.5: representa um modelo
de AI (ex.: um LLM ou um modelo de embeddings) com metadados,
requisitos e capacidades do WorkStation AI 2 que requer. As unidades
seguintes avaliam a compatibilidade com o sistema e classificam a
adequação às tarefas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ModelKind(Enum):
    """Tipo de modelo conhecido pelo sistema."""

    LLM = "llm"            # Modelo de linguagem (chat / completion)
    EMBEDDING = "embedding"  # Modelo de representações vectoriais


@dataclass(frozen=True)
class ModelRequirements:
    """Requisitos mínimos para executar um modelo.

    Valores normalizados e comparáveis com o perfil de hardware
    (HardwareProfile) e o estado de runtime (RuntimeProfile). A
    avaliação de compatibilidade pertence a unidades futuras da
    Fase 5.
    """

    min_ram_gb: float = 1.0
    min_vram_gb: float | None = None
    min_cpu_cores: int = 1
    requires_gpu: bool = False
    min_available_disk_gb: float = 0.0
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_gpu_requirement(self) -> bool:
        """Indica se o modelo exige GPU obrigatória."""
        return self.requires_gpu or self.min_vram_gb is not None


@dataclass(frozen=True)
class ModelMetadata:
    """Metadados descritivos de um modelo conhecido."""

    version: str
    params_billions: float
    context_window_tokens: int
    license: str = ""
    architecture: str = ""


@dataclass(frozen=True)
class ModelDefinition:
    """Definição estrutural de um modelo conhecido do sistema.

    Representa o contrato declarativo de um modelo que o WorkStation
    AI 2 pode disponibilizar, incluindo metadados e requisitos mínimos
    para a sua execução local.
    """

    id: str
    name: str
    description: str
    kind: ModelKind
    metadata: ModelMetadata
    requirements: ModelRequirements = field(default_factory=ModelRequirements)

    @property
    def summary(self) -> str:
        """Resumo textual do modelo para apresentação."""
        return f"{self.name} ({self.id})"


class ModelState(Enum):
    """Estados de compatibilidade de um modelo contra o sistema."""

    AVAILABLE = "available"      # Requisitos do modelo e capacidades satisfeitos
    RESTRICTED = "restricted"    # Executável, mas condicionado pelas capacidades/runtime
    UNAVAILABLE = "unavailable"  # Requisitos mínimos não satisfeitos


@dataclass(frozen=True)
class ModelCheck:
    """Resultado da verificação de um requisito de modelo individual.

    Regista o requisito (valor exigido), o que está disponível no
    sistema e se foi satisfeito, permitindo justificar o veredicto.
    """

    name: str  # "capabilities", "ram_total", "ram_available", "cpu_cores", "gpu", "disk"
    required: float | int | bool | tuple[str, ...] | None
    available: float | int | bool | tuple[str, ...] | None
    satisfied: bool


@dataclass(frozen=True)
class ModelVerdict:
    """Veredicto de compatibilidade de um modelo contra o sistema.

    Combina o estado final com as verificações por requisito que o
    justificam e com as capacidades do sistema que faltam, quando
    aplicável.
    """

    model_id: str
    state: ModelState
    checks: tuple[ModelCheck, ...] = field(default_factory=tuple)
    missing_capabilities: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_available(self) -> bool:
        """Indica se o modelo está disponível (não condicionado)."""
        return self.state == ModelState.AVAILABLE

    @property
    def summary(self) -> str:
        """Resumo textual do veredicto para apresentação."""
        labels = {
            ModelState.AVAILABLE: "disponível",
            ModelState.RESTRICTED: "condicionado",
            ModelState.UNAVAILABLE: "indisponível",
        }
        return f"{self.model_id}: {labels[self.state]}"


__all__ = [
    "ModelCheck",
    "ModelDefinition",
    "ModelKind",
    "ModelMetadata",
    "ModelRequirements",
    "ModelState",
    "ModelVerdict",
]