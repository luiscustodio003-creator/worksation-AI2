"""Fonte única de verdade dos contratos de arquitectura do kernel (KERNEL-07).

As tabelas abaixo são declaradas uma única vez e partilhadas pelos testes
de contrato arquitectural (`test_architecture_contract.py`,
`test_core_public.py` e `test_boundary_kernel.py`). Qualquer alteração a
superfícies públicas, fronteiras ou versões é deliberada e detectada no
gate de forma automática.
"""

# Aresta autorizada: subsistema origem -> subsistema destino.
FRONTEIRAS: frozenset[tuple[str, str]] = frozenset(
    {
        ("capability", "hardware"),
        ("capability", "runtime"),
        ("core", "extension"),
        ("execution", "core"),
        ("execution", "resource"),
        ("extension", "core"),
        ("extension", "security"),
        ("knowledge", "core"),
        ("model", "capability"),
        ("model", "hardware"),
        ("model", "runtime"),
        ("resource", "core"),
        ("resource", "extension"),
        ("resource", "hardware"),
        ("resource", "runtime"),
        ("runtime_engine", "core"),
        ("runtime_engine", "execution"),
        ("runtime_engine", "resource"),
        ("runtime_engine", "security"),
        ("runtime_engine", "task"),
        ("security", "core"),
        ("task", "capability"),
        ("task", "hardware"),
        ("task", "model"),
        ("task", "provider"),
        ("task", "runtime"),
    }
)

# Subsistemas funcionais previstos mas ainda não iniciados (Fases 10–11);
# knowledge foi autorizado na unidade 9.1 e saiu desta lista.
SUBSISTEMAS_FUTUROS = ("api", "ui")

# Adaptadores de plataforma: específicos de SO, de acesso reservado.
ADAPTADORES_SO = ("wsai2.platform.windows", "wsai2.platform.linux")

# Dependências exactas permitidas POR SUBSISTEMA (Dependency Firewall,
# KERNEL-04), com imports TYPE_CHECKING incluídos.
FIREWALL: dict[str, frozenset[str]] = {
    "capability": frozenset({"hardware", "runtime"}),
    "core": frozenset({"extension"}),
    "execution": frozenset({"core", "resource"}),
    "extension": frozenset({"core", "security"}),
    "hardware": frozenset(),
    "knowledge": frozenset({"core"}),
    "model": frozenset({"capability", "hardware", "runtime"}),
    "platform": frozenset(),
    "provider": frozenset(),
    "resource": frozenset({"core", "extension", "hardware", "runtime"}),
    "runtime": frozenset(),
    "runtime_engine": frozenset({"core", "execution", "resource", "security", "task"}),
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

# Superfícies públicas dos subsistemas do kernel não-folha (KERNEL-05/06).
SUPERFICIES_PUBLICAS: dict[str, frozenset[str]] = {
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

# Localização física do contrato versionado de cada subsistema do kernel.
MODULO_CONTRATO: dict[str, str] = {
    "core": "wsai2.core.public",
    "execution": "wsai2.execution",
    "resource": "wsai2.resource",
    "runtime_engine": "wsai2.runtime_engine",
    "security": "wsai2.security",
}

# Nome da constante de versão por subsistema do kernel.
CONTRATO_CONSTANTES: dict[str, str] = {
    "core": "CORE_PUBLIC_CONTRACT_VERSION",
    "execution": "EXECUTION_CONTRACT_VERSION",
    "resource": "RESOURCE_CONTRACT_VERSION",
    "runtime_engine": "RUNTIME_ENGINE_CONTRACT_VERSION",
    "security": "SECURITY_CONTRACT_VERSION",
}

# Versões sancionadas esperadas por subsistema do kernel (bumps deliberados).
CONTRACT_VERSIONES: dict[str, str] = {
    "core": "1.0",
    "execution": "1.0",
    "resource": "1.0",
    "runtime_engine": "1.0",
    "security": "1.0",
}