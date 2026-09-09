# KERNEL-02 — MAPA DE DEPENDÊNCIAS E FRONTEIRAS PÚBLICAS

**Data:** 2026-09-09
**Branch:** core-hardening-foundation
**Unidade:** KERNEL-02 — mapa formal + candidata a `core.public`
**Base:** KERNEL-01 (inventário, `docs/architecture/KERNEL-01-core-inventory.md`)
**Código alterado:** nenhum (unidade documental)
**Verificação:** 491/491 testes verdes; mapa consistente com `FRONTEIRAS`

## 1. Objectivo

Fixar o mapa real de dependências e propor a forma da superfície pública
do núcleo (`core.public`), para o KERNEL-03 materializar. Entrega apenas
evidência e proposta — não move ficheiros.

## 2. Classificação por camada arquitectural

| Camada | Subsistemas | Papel |
|---|---|---|
| Kernel (Core) | `core`, `execution`, `resource`, `runtime_engine`, `security` | Decidir, planear, governar, executar |
| Infraestrutura | `platform` | Adaptadores de SO (isolados pela Constituição) |
| Domínio | `hardware`, `runtime`, `capability`, `model`, `provider`, `task`, `knowledge` | Capacidades e estado de domínio |
| Contratos addon | `extension` | Ciclo de vida e compatibility (+ ponte de grants `extension→security`) |
| Application | — | `SUBSISTEMAS_FUTUROS = ("api", "ui")`; nenhum presente |

## 3. Mapa de dependências (arestas reais)

Grafo de imports entre subsistemas, 22 arestas autorizadas
(`FRONTEIRAS`, `tests/test_architecture_contract.py`):

```text
capability      → hardware, runtime
core            → extension
execution       → core, resource
extension       → core, security
knowledge       → core
model           → capability, hardware, runtime
resource        → core, extension, hardware, runtime
runtime_engine  → core, execution, resource, security, task
security        → core
task            → capability, hardware, model, provider, runtime
```

Grafo **acíclico** em runtime (verificação com `TYPE_CHECKING` excluído).

## 4. Consumidores reais (scan AST 2026-09-09)

| Módulo core | Consumido por |
|---|---|
| `execution` | `runtime_engine.manager`, `runtime_engine.scheduler` |
| `resource` | `runtime_engine.manager`; `resource.governor` consome `extension`+`hardware` |
| `extension` | `resource.governor` |
| `core.*` | execution, extension, knowledge, resource, runtime_engine, security |

`platform` é consumido apenas pelas fábricas de hardware/runtime (via `factory`).

## 5. Candidata a superfície pública (`core.public`)

Símbolos públicos reais que o KERNEL-03 deve formalizar como contrato
versível:

```text
core.errors        WsaiError, ValidationError, CapabilityError, ModelError,
                   ProviderError, ResourceError, TimeoutError, CancellationError,
                   PermissionError, ProjectIsolationError, ExecutionError
core.context       ExecutionContext, CancellationToken, ExecutionPriority
execution.base     TimeoutPolicy, RecoveryPolicy
execution.runner   run_with_timeout, run_with_recovery, execute_with_policies
resource           ResourceGovernor, ResourceCheck, ResourceBudgetResult
runtime_engine     Scheduler, MultilayerExecutionQueue, RuntimeManager,
                   ExecutionMonitor, SchedulerReport, priority_for_plan
security           PolicyEngine, Principal, PolicyDecision,
                   require_project, assert_same_project
```

A **decisão do conjunto definitivo** (incluindo o que permanece `internal`)
é do KERNEL-03, com base nesta lista.

## 6. Nós de atenção

- **P3 — `runtime_engine`**: 5 arestas de saída — nó de maior raio de impacto; priorizar contrato antes de qualquer MOVE.
- **P3 — `resource.governor→hardware`**: acoplamento entre governação e capacidade — reavaliar na definição do `core.public` (KERNEL-03), sem acção agora.
- **P3 — observability**: `ExecutionMonitor`/`MonitorSnapshot` existem sem API pública de métricas transversal — tema do KERNEL-06.

## 7. Uso

- Entrada obrigatória do **KERNEL-03** (Core Public Contract).
- Verificação contínua contra `FRONTEIRAS` na suíte (contrato arquitectural).

## 8. Conclusão

Unidade documental KERNEL-02 **concluída** sem alteração de código.
Suíte completa: **491/491 verdes**.