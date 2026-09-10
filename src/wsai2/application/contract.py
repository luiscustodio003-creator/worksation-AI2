"""Contratos puros de use-case da camada Application (APP-02, unidade APP-02).

Reúne as mensagens de pedido/resposta dos use-cases do Ramo A. Estes
contratos são a fronteira estável que a API e a futura UI consomem
(constituição, artigo 7: «a interface apresenta capacidades reais e
consome contratos da aplicação»).

Regras formais:

- cada contrato é um ``@dataclass(frozen=True)`` — imutável e puro, sem
  estado oculto;
- os tipos de domínio are consumidos ao nível do pacote (wsai2.<sub>),
  nunca de módulos internos, respeitando a fronteira arquitectural;
- não existe lógica central de decisão: a Application apenas tipa os
  payloads já produzidos pelo núcleo e subsistemas de domínio;
- nenhum contrato efectua I/O, transporte ou persistência.

As mensagens estão agrupadas por use-case: System/Platform (APP-03),
Hardware (APP-04), Runtime (APP-05), Capabilities (APP-06), Models
(APP-07), Tasks (APP-08), Knowledge (APP-09) e Execution/Status/
Cancellation (APP-10).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from wsai2.capability import CompatibilityReport
from wsai2.core.public import ExecutionPriority
from wsai2.hardware import CapabilityDomain, HardwareProfile
from wsai2.knowledge import KnowledgeContext, KnowledgeKind, KnowledgeRecord
from wsai2.model import ModelCategory, ModelVerdict
from wsai2.platform import PlatformInfo
from wsai2.runtime import RuntimeProfile, SystemUptime
from wsai2.runtime_engine import (
    ExecutionReport,
    ExecutionSnapshot,
    ExecutionStatus,
)
from wsai2.task import (
    ExecutionPlan,
    Task,
    TaskCapabilitySelection,
    TaskClassification,
    TaskRequirements,
)


# --- System/Platform (APP-03) ---


@dataclass(frozen=True)
class SystemInfoRequest:
    """Pedido do use-case de informação do sistema (APP-03).

    Não possui parâmetros de entrada; a resposta devolve a plataforma e o
    uptime actuais recolhidos pelos subsistemas de domínio.
    """


@dataclass(frozen=True)
class SystemInfoResponse:
    """Resposta do use-case de informação do sistema.

    Attributes:
        platform: superfície pública ``PlatformInfo`` da plataforma.
        uptime: uptime do sistema, quando disponível.
    """

    platform: PlatformInfo
    uptime: SystemUptime | None = None


# --- Hardware (APP-04) ---


@dataclass(frozen=True)
class HardwareProfileRequest:
    """Pedido do use-case de perfil de hardware (APP-04).

    Não possui parâmetros; o perfil estrutural é devolvido pelo domínio
    de hardware sem filtros.
    """


@dataclass(frozen=True)
class HardwareProfileResponse:
    """Resposta do use-case de perfil de hardware.

    Attributes:
        profile: superfície pública ``HardwareProfile`` da máquina actual.
    """

    profile: HardwareProfile


# --- Runtime (APP-05) ---


@dataclass(frozen=True)
class RuntimeProfileRequest:
    """Pedido do use-case de estado de runtime (APP-05).

    Não possui parâmetros; o estado momentâneo é devolvido pelo domínio
    de runtime sem filtros.
    """


@dataclass(frozen=True)
class RuntimeProfileResponse:
    """Resposta do use-case de estado de runtime.

    Attributes:
        profile: superfície pública ``RuntimeProfile`` (estado actual).
    """

    profile: RuntimeProfile


# --- Capabilities (APP-06) ---


@dataclass(frozen=True)
class CapabilitiesRequest:
    """Pedido do use-case de capacidades (APP-06).

    Attributes:
        domain: filtro opcional por domínio de capacidade.
    """

    domain: CapabilityDomain | None = None


@dataclass(frozen=True)
class CapabilitiesResponse:
    """Resposta do use-case de capacidades.

    Attributes:
        report: relatório de compatibilidade com as capacidades
            disponíveis (superfície pública de ``wsai2.capability``).
    """

    report: CompatibilityReport


# --- Models (APP-07) ---


@dataclass(frozen=True)
class ModelsRequest:
    """Pedido do use-case de modelo (APP-07).

    Attributes:
        category: filtro opcional por categoria de modelo.
    """

    category: ModelCategory | None = None


@dataclass(frozen=True)
class ModelsResponse:
    """Resposta do use-case de modelo.

    Attributes:
        verdicts: veredictos por modelo avaliado; vazio quando nenhum
            modelo corresponde ao filtro.
    """

    verdicts: tuple[ModelVerdict, ...] = field(default_factory=tuple)


# --- Tasks (APP-08) ---


@dataclass(frozen=True)
class TaskAnalysisRequest:
    """Pedido do use-case de tarefa (APP-08).

    Attributes:
        task: tarefa a classificar e planear (superfície ``Task``).
    """

    task: Task


@dataclass(frozen=True)
class TaskAnalysisResponse:
    """Resposta do use-case de tarefa.

    Attributes:
        task_id: identificador da tarefa analisada.
        classification: classificação da tarefa (tipo e categoria).
        requirements: requisitos derivados da tarefa.
        selection: selecção de capacidades quando a tarefa é exequível.
        plan: plano de execução quando foi possível planear.
    """

    task_id: str
    classification: TaskClassification
    requirements: TaskRequirements
    selection: TaskCapabilitySelection | None = None
    plan: ExecutionPlan | None = None


# --- Knowledge (APP-09) ---


@dataclass(frozen=True)
class KnowledgeContextRequest:
    """Pedido do use-case de conhecimento (APP-09).

    Attributes:
        query: consulta de texto do utilizador para pesquisa de contexto.
        limit: máximo de registos devolvidos.
        kind: filtro opcional por tipo de registo de conhecimento.
    """

    query: str
    limit: int = 8
    kind: KnowledgeKind | None = None

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("a consulta de conhecimento não pode ser vazia")
        if self.limit <= 0:
            raise ValueError("o limite de registos deve ser positivo")


@dataclass(frozen=True)
class KnowledgeContextResponse:
    """Resposta do use-case de conhecimento.

    Attributes:
        query: consulta original (espelhada para associação pedido/resposta).
        matches: registos de conhecimento correspondentes.
        context: contexto de conhecimento construído, quando disponível.
    """

    query: str
    matches: tuple[KnowledgeRecord, ...] = field(default_factory=tuple)
    context: KnowledgeContext | None = None


# --- Execution / Status / Cancellation (APP-10) ---


@dataclass(frozen=True)
class ExecutionRequest:
    """Pedido do use-case de execução (APP-10).

    Attributes:
        task: tarefa a executar.
        priority: prioridade de execução (padrão: ``NORMAL``).
        timeout_seconds: tempo máximo de execução, quando limitado.
    """

    task: Task
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("o timeout deve ser positivo")


@dataclass(frozen=True)
class ExecutionResponse:
    """Resposta do use-case de execução.

    Attributes:
        task_id: identificador da tarefa executada.
        plan: plano devolvido pelo escalonador, quando existir.
        report: relatório de execução, quando a execução está concluída.
    """

    task_id: str
    plan: ExecutionPlan | None = None
    report: ExecutionReport | None = None


@dataclass(frozen=True)
class ExecutionStatusRequest:
    """Pedido de estado de uma execução (APP-10).

    Attributes:
        execution_id: identificador da execução.
    """

    execution_id: str

    def __post_init__(self) -> None:
        if not self.execution_id.strip():
            raise ValueError("o identificador de execução não pode ser vazio")


@dataclass(frozen=True)
class ExecutionStatusResponse:
    """Resposta de estado de uma execução.

    Attributes:
        execution_id: identificador da execução.
        status: estado global da execução, quando conhecido.
        snapshot: fotografia do estado em curso, quando existir.
        report: relatório final, quando a execução está concluída.
    """

    execution_id: str
    status: ExecutionStatus | None = None
    snapshot: ExecutionSnapshot | None = None
    report: ExecutionReport | None = None


@dataclass(frozen=True)
class CancellationRequest:
    """Pedido de cancelamento de uma execução (APP-10).

    Attributes:
        execution_id: identificador da execução a cancelar.
    """

    execution_id: str

    def __post_init__(self) -> None:
        if not self.execution_id.strip():
            raise ValueError("o identificador de execução não pode ser vazio")


@dataclass(frozen=True)
class CancellationResponse:
    """Resposta de cancelamento de uma execução.

    Attributes:
        execution_id: identificador da execução cancelada.
        cancelled: True quando o cancelamento foi aplicado.
    """

    execution_id: str
    cancelled: bool