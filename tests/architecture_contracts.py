"""Fonte única de verdade dos contratos de arquitectura do kernel (KERNEL-07).

As tabelas abaixo são declaradas uma única vez e partilhadas pelos testes
de contrato arquitectural (`test_architecture_contract.py`,
`test_core_public.py` e `test_boundary_kernel.py`). Qualquer alteração a
superfícies públicas, fronteiras ou versões é deliberada e detectada no
gate de forma automática.
"""

# Aresta autorizada: subsistema origem -> subsistema destino.
# KERNEL-09: a implementação pesada desceu para `infrastructure`; os
# pacotes resource/runtime_engine tornaram-se shells de re-export.
FRONTEIRAS: frozenset[tuple[str, str]] = frozenset(
    {
        ("api", "application"),
        ("api", "core"),
        ("application", "capability"),
        ("application", "core"),
        ("application", "hardware"),
        ("application", "knowledge"),
        ("application", "model"),
        ("application", "platform"),
        ("application", "runtime"),
        ("application", "runtime_engine"),
        ("application", "task"),
        ("capability", "hardware"),
        ("capability", "runtime"),
        ("core", "extension"),
        ("execution", "core"),
        ("execution", "resource"),
        ("extension", "core"),
        ("extension", "security"),
        ("infrastructure", "core"),
        ("infrastructure", "execution"),
        ("infrastructure", "extension"),
        ("infrastructure", "hardware"),
        ("infrastructure", "runtime"),
        ("infrastructure", "security"),
        ("infrastructure", "task"),
        ("knowledge", "core"),
        ("model", "capability"),
        ("model", "hardware"),
        ("model", "runtime"),
        ("resource", "infrastructure"),
        ("runtime_engine", "infrastructure"),
        ("security", "core"),
        ("task", "capability"),
        ("task", "hardware"),
        ("task", "model"),
        ("task", "provider"),
        ("task", "runtime"),
    }
)

# Subsistemas funcionais previstos mas ainda não iniciados (Fases 10–11);
# knowledge foi autorizado na unidade 9.1 e saiu desta lista; api foi
# autorizado na unidade API-01 (Fase 10) e saiu desta lista.
SUBSISTEMAS_FUTUROS = ("ui",)

# Adaptadores de plataforma: específicos de SO, de acesso reservado.
ADAPTADORES_SO = ("wsai2.platform.windows", "wsai2.platform.linux")

# Dependências exactas permitidas POR SUBSISTEMA (Dependency Firewall,
# KERNEL-04), com imports TYPE_CHECKING incluídos.
FIREWALL: dict[str, frozenset[str]] = {
    "api": frozenset({"application", "core"}),
    "application": frozenset({"capability", "core", "hardware", "knowledge", "model", "platform", "runtime", "runtime_engine", "task"}),
    "capability": frozenset({"hardware", "runtime"}),
    "core": frozenset({"extension"}),
    "execution": frozenset({"core", "resource"}),
    "extension": frozenset({"core", "security"}),
    "hardware": frozenset(),
    "infrastructure": frozenset({"core", "execution", "extension", "hardware", "runtime", "security", "task"}),
    "knowledge": frozenset({"core"}),
    "model": frozenset({"capability", "hardware", "runtime"}),
    "platform": frozenset(),
    "provider": frozenset(),
    "resource": frozenset({"infrastructure"}),
    "runtime": frozenset(),
    "runtime_engine": frozenset({"infrastructure"}),
    "security": frozenset({"core"}),
    "task": frozenset({"capability", "hardware", "model", "provider", "runtime"}),
}

# Subsistemas do kernel (Core / Execution & Intelligence Kernel, KERNEL-01).
KERNEL_SUBSISTEMAS = ("core", "execution", "resource", "runtime_engine", "security")

# Superfície pública de `wsai2.core.public` (KERNEL-03): 14 símbolos + versão.
CORE_PUBLIC_SUPERFICIE: frozenset[str] = frozenset(
    {
        "CORE_PUBLIC_CONTRACT_VERSION",
        "CancellationToken",
        "CapabilityError",
        "CancellationError",
        "ExecutionContext",
        "ExecutionError",
        "ExecutionPriority",
        "ModelError",
        "PermissionError",
        "ProjectIsolationError",
        "ProviderError",
        "ResourceError",
        "TimeoutError",
        "ValidationError",
        "WsaiError",
    }
)

# Superfícies públicas dos subsistemas do kernel não-folha (KERNEL-05/06),
# da camada Application (APP-02) e da API (API-01).
SUPERFICIES_PUBLICAS: dict[str, frozenset[str]] = {
    "api": frozenset(
        {
            "ApiGateway",
            "ApiRequest",
            "ApiResponse",
            "StdLibHttpGateway",
            "capabilities",
            "hardware",
            "health",
            "models",
            "runtime",
            "system",
        }
    ),
    "application": frozenset(
        {
            "CancellationRequest",
            "CancellationResponse",
            "CancellationService",
            "CapabilitiesRequest",
            "CapabilitiesResponse",
            "CapabilitiesService",
            "ExecutionRequest",
            "ExecutionResponse",
            "ExecutionService",
            "ExecutionStatusRequest",
            "ExecutionStatusResponse",
            "ExecutionStatusService",
            "HardwareProfileRequest",
            "HardwareProfileResponse",
            "HardwareProfileService",
            "KnowledgeContextRequest",
            "KnowledgeContextResponse",
            "KnowledgeContextService",
            "ModelsRequest",
            "ModelsResponse",
            "ModelsService",
            "RuntimeProfileRequest",
            "RuntimeProfileResponse",
            "RuntimeProfileService",
            "SystemInfoRequest",
            "SystemInfoResponse",
            "SystemInfoService",
            "TaskAnalysisRequest",
            "TaskAnalysisResponse",
            "TaskAnalysisService",
        }
    ),
    "execution": frozenset(
        {
            "DeadlineGuard",
            "RecoveryPolicy",
            "RetryAttempt",
            "TimeoutPolicy",
            "execute_with_policies",
            "run_with_recovery",
            "run_with_timeout",
        }
    ),
    "resource": frozenset(
        {
            "AllocationState",
            "ResourceAllocation",
            "ResourceBudgetResult",
            "ResourceCheck",
            "ResourceDimension",
            "ResourceGovernor",
            "ResourceVerdict",
        }
    ),
    "security": frozenset(
        {
            "PolicyDecision",
            "PolicyEngine",
            "Principal",
            "assert_same_project",
            "denied_decision",
            "require_project",
        }
    ),
    "runtime_engine": frozenset(
        {
            "ExecutionMonitor",
            "ExecutionReport",
            "ExecutionSnapshot",
            "ExecutionStatus",
            "MonitorSnapshot",
            "MultilayerExecutionQueue",
            "QueueItem",
            "QueueSnapshot",
            "RuntimeManager",
            "ScheduleOutcome",
            "Scheduler",
            "SchedulerReport",
            "StepOutcome",
            "StepRunner",
            "StepStatus",
            "priority_for_plan",
        }
    ),
}

# Subcontrato de observabilidade (KERNEL-06): fracção da superfície de
# governação que é a fronteira transversal de métricas (target sec. 3.5).
OBSERVABILIDADE_SUPERFICIE: frozenset[str] = frozenset(
    {
        "ExecutionMonitor",
        "ExecutionReport",
        "ExecutionSnapshot",
        "ExecutionStatus",
        "MonitorSnapshot",
        "ScheduleOutcome",
        "SchedulerReport",
        "StepOutcome",
        "StepRunner",
        "StepStatus",
    }
)

GOVERNO_SUPERFICIE: frozenset[str] = frozenset(
    {
        "MultilayerExecutionQueue",
        "QueueItem",
        "QueueSnapshot",
        "RuntimeManager",
        "Scheduler",
        "priority_for_plan",
    }
)

# Localização física do contrato versionado de cada subsistema do kernel
# e da camada Application.
MODULO_CONTRATO: dict[str, str] = {
    "api": "wsai2.api",
    "application": "wsai2.application",
    "core": "wsai2.core.public",
    "execution": "wsai2.execution",
    "resource": "wsai2.resource",
    "runtime_engine": "wsai2.runtime_engine",
    "security": "wsai2.security",
}

# Nome da constante de versão por subsistema do kernel.
CONTRATO_CONSTANTES: dict[str, str] = {
    "api": "API_CONTRACT_VERSION",
    "application": "APPLICATION_CONTRACT_VERSION",
    "core": "CORE_PUBLIC_CONTRACT_VERSION",
    "execution": "EXECUTION_CONTRACT_VERSION",
    "resource": "RESOURCE_CONTRACT_VERSION",
    "runtime_engine": "RUNTIME_ENGINE_CONTRACT_VERSION",
    "security": "SECURITY_CONTRACT_VERSION",
}

# Versões sancionadas esperadas por subsistema do kernel (bumps deliberados).
CONTRACT_VERSIONES: dict[str, str] = {
    "api": "1.0",
    "application": "1.0",
    "core": "1.0",
    "execution": "1.0",
    "resource": "1.0",
    "runtime_engine": "1.0",
    "security": "1.0",
}

# Contrato de addon (KERNEL-10): superfície congelada de `wsai2.extension`,
# a camada que define o contrato dos addons do WorkStation AI 2. Permanece
# fora de `KERNEL_SUBSISTEMAS` — é a fronteira addon→kernel, não um subsistema
# do núcleo. `SUPPORTED_CONTRACT_VERSION` fica na superfície por desígnio (é o
# número semântico do contrato addon→core). Projects é um addon futuro (alvo,
# sec. 9) e não recebe código do kernel.
ADDON_CONTRATO_MODULO = "wsai2.extension"
ADDON_CONTRATO_SUPERFICIE: frozenset[str] = frozenset(
    {
        "ContractVersion",
        "ExtensionContract",
        "ExtensionKind",
        "ExtensionLifecycleState",
        "ExtensionRegistry",
        "ResourceLimit",
        "SUPPORTED_CONTRACT_VERSION",
        "can_transition",
        "transition",
        "valid_transitions",
    }
)
ADDON_CONTRATO_CONSTANTE_VERSION = "EXTENSION_CONTRACT_VERSION"
ADDON_CONTRATO_VERSION = "1.0"