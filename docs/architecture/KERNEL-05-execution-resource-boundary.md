# KERNEL-05 — RESOURCE / EXECUTION BOUNDARY

- **Data:** 2026-09-09
- **Unidade:** KERNEL-05 (secção 12 de `CORE_KERNEL_TARGET.md`)
- **Estado:** CONCLUÍDA
- **Decisão:** Opção A — a fronteira é o próprio `__init__` de cada subsistema; sem fachadas novas.
- **Ficheiros alterados:** `src/wsai2/{execution,resource,security}/__init__.py`, `tests/test_boundary_kernel.py` (novo), `docs/project/PROJECT_STATE.md`, `docs/project/IMPLEMENTATION_LOG.md`, `docs/architecture/CORE_KERNEL_TARGET.md`, este relatório.

## Objectivo

Definir e **fixar** as superfícies públicas de `execution`, `resource` e
`security` — os três subsistemas do kernel com consumidores reais — com
versão de contrato e detecção automática de qualquer alteração.

## Decisão: Opção A vs B

- **Opção A (adoptada):** a superfície pública é o `__all__` do `__init__`
  de cada subsistema + constante de versão; teste de contrato que congela
  os símbolos e impõe consumidores apenas ao nível do pacote.
- **Opção B (rejeitada):** criar `execution/public.py`, `resource/public.py`
  e `security/public.py` espelhando `core.public`. Duplicaria a superfície
  (drift entre ficheiros), acrescentaria três módulos sem ganho e obrigaria
  ao churn de migração no KERNEL-08 com a mesma garantia.
- **Porque não se replica `core.public`:** `core` é a folha alcançada por
  todos; o agregador único é aí o ponto de entrada sancionado. Os outros
  subsistemas do kernel são camadas internas com poucos consumidores que já
  importam ao nível do pacote (`from wsai2.execution import …`).

## Contratos de fronteira (versão 1.0)

| Fronteira | Versão | Superfície pública (`__all__`) sancionada |
| --- | --- | --- |
| execution | `EXECUTION_CONTRACT_VERSION = "1.0"` | DeadlineGuard, RecoveryPolicy, RetryAttempt, TimeoutPolicy, execute_with_policies, run_with_recovery, run_with_timeout |
| resource | `RESOURCE_CONTRACT_VERSION = "1.0"` | AllocationState, ResourceAllocation, ResourceBudgetResult, ResourceCheck, ResourceDimension, ResourceGovernor, ResourceVerdict |
| security | `SECURITY_CONTRACT_VERSION = "1.0"` | PolicyDecision, PolicyEngine, Principal, assert_same_project, denied_decision, require_project |

Qualquer alteração à superfície exige bump da versão (major para remoções)
e é detectada automaticamente no gate.

## Consumidores reais (scan AST 2026-09-09)

- `execution` ← `runtime_engine.manager` (`execute_with_policies`; typing: RecoveryPolicy, TimeoutPolicy), `runtime_engine.scheduler` (typing: RecoveryPolicy, TimeoutPolicy).
- `resource` ← `execution.runner` (typing: ResourceGovernor, ResourceAllocation), `runtime_engine.manager` (typing: ResourceGovernor) — consumo actual apenas tipográfico; a aresta `execution→resource` mantém-se para o enforce runtime.
- `security` ← `extension.registry` (PolicyEngine), `runtime_engine.{scheduler,manager}` (PolicyEngine, denied_decision; typing PolicyDecision).

Todos os consumidores em `src` importam **ao nível do pacote** — a regra é
imposta por teste e visa impedir importações de módulos internos.

## Regra de fronteira

1. Consumidores externos importam apenas `wsai2.<fronteira>` (pacote).
2. Módulos internos (`base`, `runner`, `governor`, `policy`, …) não são
   alcançáveis por consumidores de outro subsistema.
3. O `core.public` permanece o único agregador explícito (folha `core`).
4. `runtime_engine` (superfície + observabilidade) fica para o **KERNEL-06**.

## Detecção automática

Novo `tests/test_boundary_kernel.py`:

- `test_versao_de_contrato_valida_e_major_minor` — versões na forma `major.minor`.
- `test_superficies_publicas_congeladas` — `__all__` == superfície sancionada; versão fora da superfície.
- `test_consumidores_apenas_ao_nivel_do_pacote` — AST sobre `src`: sem import de `wsai2.<fronteira>.<módulo interno>` por consumidores externos.

## Validação

```text
py -3.12 -m pytest
tests=500  failures=0  errors=0  skipped=0
```

(500 = 497 + 3 testes de fronteira; `FIREWALL` e aciclicidade intactos — zero arestas novas.)

## Próximo passo

`/wsai-plan KERNEL-06` — Observability boundary (superfície de observabilidade e fronteira de governação de `runtime_engine`).