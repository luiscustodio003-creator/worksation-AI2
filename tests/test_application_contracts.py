"""Testes dos contratos de use-case da camada Application (APP-02).

Verifica que cada contrato é uma dataclass congelada, reutiliza os tipos
públicos de domínio nas mensagens (REUSE, constituição artigo 6) e impõe
as regras mínimas de validação documentadas. Nenhum contrato contém
lógica central de negócio: a Application tipa apenas payloads produzidos
pelo núcleo e subsistemas de domínio.
"""

import dataclasses

import pytest

import wsai2.application
from wsai2.application import (
    CancellationRequest,
    CancellationResponse,
    CapabilitiesRequest,
    CapabilitiesResponse,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatusRequest,
    ExecutionStatusResponse,
    HardwareProfileRequest,
    HardwareProfileResponse,
    KnowledgeContextRequest,
    KnowledgeContextResponse,
    ModelsRequest,
    ModelsResponse,
    RuntimeProfileRequest,
    RuntimeProfileResponse,
    SystemInfoRequest,
    SystemInfoResponse,
    TaskAnalysisRequest,
    TaskAnalysisResponse,
)

from wsai2.capability import CompatibilityReport
from wsai2.core.public import ExecutionPriority
from wsai2.hardware import CapabilityDomain, discover_hardware
from wsai2.knowledge import (
    KnowledgeContext,
    KnowledgeKind,
    KnowledgeRecord,
)
from wsai2.model import ModelCategory, ModelState, ModelVerdict
from wsai2.platform import OperatingSystem, PlatformInfo, get_platform
from wsai2.runtime import RuntimeProfile, SystemUptime, discover_runtime
from wsai2.runtime_engine import ExecutionStatus
from wsai2.task import (
    ExecutionPlan,
    Task,
    TaskCapabilitySelection,
    TaskClassification,
    TaskKind,
    TaskRequirements,
)

CONTRATOS = (
    SystemInfoRequest,
    SystemInfoResponse,
    HardwareProfileRequest,
    HardwareProfileResponse,
    RuntimeProfileRequest,
    RuntimeProfileResponse,
    CapabilitiesRequest,
    CapabilitiesResponse,
    ModelsRequest,
    ModelsResponse,
    TaskAnalysisRequest,
    TaskAnalysisResponse,
    KnowledgeContextRequest,
    KnowledgeContextResponse,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatusRequest,
    ExecutionStatusResponse,
    CancellationRequest,
    CancellationResponse,
)

NOMES_CONTRATOS = frozenset(wsai2.application.__all__)


def test_superficie_application_contem_20_contratos() -> None:
    """APP-02/03: a superfície expõe os 20 contratos + o serviço System.

    A constante de versão não faz parte do ``__all__`` (padrão dos
    subsistemas congelados), e não existem símbolos fora da superfície.
    """
    esperados = {c.__name__ for c in CONTRATOS} | {
        "CapabilitiesService",
        "HardwareProfileService",
        "RuntimeProfileService",
        "SystemInfoService",
    }
    assert set(NOMES_CONTRATOS) == esperados
    assert wsai2.application.APPLICATION_CONTRACT_VERSION == "1.0"
    assert "APPLICATION_CONTRACT_VERSION" not in NOMES_CONTRATOS
    for nome in NOMES_CONTRATOS:
        assert hasattr(wsai2.application, nome)


def test_contratos_sao_dataclasses_imutaveis() -> None:
    """Cada contrato é uma dataclass congelada (imutável)."""
    for contrato in CONTRATOS:
        assert dataclasses.is_dataclass(contrato)
        instancia = _instancia_do(contrato)
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(instancia, "_campo_ilegal", 1)


def _instancia_do(contrato: type) -> object:
    """Constrói uma instância mínima de um contrato para testes de imutabilidade."""
    construtores = {
        SystemInfoRequest: lambda: SystemInfoRequest(),
        SystemInfoResponse: lambda: SystemInfoResponse(platform=_plataforma()),
        HardwareProfileRequest: lambda: HardwareProfileRequest(),
        HardwareProfileResponse: lambda: HardwareProfileResponse(profile=_perfil_hardware()),
        RuntimeProfileRequest: lambda: RuntimeProfileRequest(),
        RuntimeProfileResponse: lambda: RuntimeProfileResponse(profile=_perfil_runtime()),
        CapabilitiesRequest: lambda: CapabilitiesRequest(),
        CapabilitiesResponse: lambda: CapabilitiesResponse(report=_relatorio_compatibilidade()),
        ModelsRequest: lambda: ModelsRequest(),
        ModelsResponse: lambda: ModelsResponse(),
        TaskAnalysisRequest: lambda: TaskAnalysisRequest(task=_tarefa()),
        TaskAnalysisResponse: lambda: TaskAnalysisResponse(
            task_id="t1", classification=_classificacao(), requirements=_requisitos()
        ),
        KnowledgeContextRequest: lambda: KnowledgeContextRequest(query="q"),
        KnowledgeContextResponse: lambda: KnowledgeContextResponse(query="q"),
        ExecutionRequest: lambda: ExecutionRequest(task=_tarefa()),
        ExecutionResponse: lambda: ExecutionResponse(task_id="t1"),
        ExecutionStatusRequest: lambda: ExecutionStatusRequest(execution_id="e1"),
        ExecutionStatusResponse: lambda: ExecutionStatusResponse(execution_id="e1"),
        CancellationRequest: lambda: CancellationRequest(execution_id="e1"),
        CancellationResponse: lambda: CancellationResponse(execution_id="e1", cancelled=False),
    }
    return construtores[contrato]()


def _perfil_hardware():
    return discover_hardware()


def _perfil_runtime():
    return discover_runtime()


def _plataforma() -> PlatformInfo:
    return get_platform().detect()


def _tarefa() -> Task:
    return Task(id="t1", kind=TaskKind.CHAT, prompt="resumo do documento")


def _classificacao() -> TaskClassification:
    return TaskClassification(task_id="t1", kind=TaskKind.CHAT, category=ModelCategory.CHAT)


def _requisitos() -> TaskRequirements:
    return TaskRequirements(
        task_id="t1",
        category=ModelCategory.CHAT,
        required_capabilities=("compute",),
        max_tokens=256,
    )


def _seleccao() -> TaskCapabilitySelection:
    return TaskCapabilitySelection(
        task_id="t1",
        required=("compute",),
        available=("compute",),
        missing=(),
    )


def _plano() -> ExecutionPlan:
    return ExecutionPlan(
        task_id="t1",
        category="chat",
        feasible=True,
        model_id="m1",
        provider_id="p1",
        reasons=("recursos suficientes",),
        steps=("gerar resposta",),
    )


def _relatorio_compatibilidade() -> CompatibilityReport:
    return CompatibilityReport(hardware=_perfil_hardware(), runtime=_perfil_runtime())


def test_pedidos_sem_parametros_sao_construiveis() -> None:
    """APP-03/04/05: os pedidos de informação não exigem parâmetros."""
    assert SystemInfoRequest() is not None
    assert HardwareProfileRequest() is not None
    assert RuntimeProfileRequest() is not None


def test_system_info_resposta_carrega_plataforma_e_uptime() -> None:
    """APP-03: devolve ``PlatformInfo`` e ``SystemUptime`` reutilizados."""
    resposta = SystemInfoResponse(platform=_plataforma())
    assert isinstance(resposta.platform, PlatformInfo)
    assert resposta.platform.os is OperatingSystem.WINDOWS
    assert resposta.uptime is None

    uptime = SystemUptime(boot_timestamp=1.0, uptime_seconds=42.0)
    resposta = SystemInfoResponse(platform=_plataforma(), uptime=uptime)
    assert resposta.uptime is uptime


def test_hardware_resposta_carrega_perfil_estrutural() -> None:
    """APP-04: a resposta tipa o ``HardwareProfile`` do domínio."""
    perfil = _perfil_hardware()
    resposta = HardwareProfileResponse(profile=perfil)
    assert resposta.profile is perfil
    assert resposta.profile.memory.total_bytes > 0


def test_runtime_resposta_carrega_estado_momentaneo() -> None:
    """APP-05: a resposta tipa o ``RuntimeProfile`` do domínio."""
    resposta = RuntimeProfileResponse(profile=discover_runtime())
    assert isinstance(resposta.profile, RuntimeProfile)
    assert resposta.profile.cpu.percent >= 0


def test_capabilities_pedido_filtra_por_dominio() -> None:
    """APP-06: filtro opcional por domínio de capacidade."""
    assert CapabilitiesRequest().domain is None
    pedido = CapabilitiesRequest(domain=CapabilityDomain.GRAPHICS)
    assert pedido.domain is CapabilityDomain.GRAPHICS


def test_capabilities_resposta_carrega_relatorio() -> None:
    """APP-06: a resposta tipa o relatório de compatibilidade."""
    resposta = CapabilitiesResponse(report=_relatorio_compatibilidade())
    assert isinstance(resposta.report, CompatibilityReport)


def test_models_resposta_padrao_vazio_e_com_veredictos() -> None:
    """APP-07: lista de veredictos vazia por defeito e tipada por modelo."""
    assert ModelsResponse().verdicts == ()
    assert ModelsRequest().category is None

    veredicto = ModelVerdict(model_id="m1", state=ModelState.AVAILABLE)
    resposta = ModelsResponse(verdicts=(veredicto,))
    assert resposta.verdicts == (veredicto,)
    assert ModelsRequest(category=ModelCategory.CHAT).category is ModelCategory.CHAT


def test_task_analysis_resposta_completa_e_filtravel() -> None:
    """APP-08: classificação, requisitos, selecção e plano reutilizados."""
    pedido = TaskAnalysisRequest(task=_tarefa())
    assert pedido.task.id == "t1"

    resposta = TaskAnalysisResponse(
        task_id="t1",
        classification=_classificacao(),
        requirements=_requisitos(),
        selection=_seleccao(),
        plan=_plano(),
    )
    assert resposta.classification.kind is TaskKind.CHAT
    assert resposta.requirements.max_tokens == 256
    assert resposta.selection.missing == ()
    assert resposta.plan.feasible is True

    sem_plano = TaskAnalysisResponse(
        task_id="t1",
        classification=_classificacao(),
        requirements=_requisitos(),
    )
    assert sem_plano.selection is None
    assert sem_plano.plan is None


def test_knowledge_consulta_valida_texto_e_limite() -> None:
    """APP-09: consulta não pode ser vazia e o limite deve ser positivo."""
    pedido = KnowledgeContextRequest(query="como configurar", limit=5)
    assert pedido.limit == 5
    assert pedido.kind is None

    with pytest.raises(ValueError):
        KnowledgeContextRequest(query="   ")
    with pytest.raises(ValueError):
        KnowledgeContextRequest(query="válida", limit=0)


def test_knowledge_resposta_carrega_registos_e_contexto() -> None:
    """APP-09: a resposta tipa registos e contexto de conhecimento."""
    registo = KnowledgeRecord(
        id="r1", title="guia", content="passos", kind=KnowledgeKind.DOCUMENT
    )
    contexto = KnowledgeContext(query="config", entries=())
    resposta = KnowledgeContextResponse(
        query="config", matches=(registo,), context=contexto
    )
    assert resposta.matches == (registo,)
    assert isinstance(resposta.context, KnowledgeContext)

    vazia = KnowledgeContextResponse(query="config")
    assert vazia.matches == ()
    assert vazia.context is None


def test_execution_pedido_prioridade_padrao_e_timeout() -> None:
    """APP-10: prioridade NORMAL por defeito e timeout validado."""
    pedido = ExecutionRequest(task=_tarefa())
    assert pedido.priority is ExecutionPriority.NORMAL
    assert pedido.timeout_seconds is None

    pedido = ExecutionRequest(task=_tarefa(), priority=ExecutionPriority.HIGH, timeout_seconds=30.0)
    assert pedido.timeout_seconds == 30.0

    with pytest.raises(ValueError):
        ExecutionRequest(task=_tarefa(), timeout_seconds=0)


def test_execution_resposta_tipada() -> None:
    """APP-10: resposta de execução devolve plano e relatório opcionais."""
    resposta = ExecutionResponse(task_id="t1", plan=_plano())
    assert resposta.task_id == "t1"
    assert resposta.plan.feasible is True
    assert resposta.report is None


def test_execution_status_e_cancelamento_validam_identificador() -> None:
    """APP-10: identificadores de execução não podem ser vazios."""
    with pytest.raises(ValueError):
        ExecutionStatusRequest(execution_id=" ")
    with pytest.raises(ValueError):
        CancellationRequest(execution_id="")

    resposta = ExecutionStatusResponse(execution_id="e1", status=ExecutionStatus.SUCCESS)
    assert resposta.status is ExecutionStatus.SUCCESS
    assert resposta.snapshot is None
    assert resposta.report is None

    cancelamento = CancellationResponse(execution_id="e1", cancelled=True)
    assert cancelamento.cancelled is True