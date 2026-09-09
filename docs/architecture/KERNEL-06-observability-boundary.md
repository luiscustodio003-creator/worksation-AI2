# KERNEL-06 — OBSERVABILITY BOUNDARY

- **Data:** 2026-09-09
- **Unidade:** KERNEL-06 (secção 12 de `CORE_KERNEL_TARGET.md`)
- **Estado:** CONCLUÍDA
- **Regra aplicada:** superfície vs. implementação pesada (KERNEL-08/09 move o peso; este fixa a superfície).
- **Ficheiros alterados:** `src/wsai2/runtime_engine/__init__.py`, `tests/test_boundary_kernel.py`, `docs/project/PROJECT_STATE.md`, `docs/project/IMPLEMENTATION_LOG.md`, `docs/architecture/CORE_KERNEL_TARGET.md`, este relatório.

## Objectivo

Fixar a **fronteira de observabilidade** do `runtime_engine`: a superfície
sancionada (reportes pós-facto + estados em curso + integração) versionada
e congelada por teste, **sem** descer a implementação pesada (colecção de
métricas) neste momento.

## Contrato de governação (versão 1.0)

`RUNTIME_ENGINE_CONTRACT_VERSION = "1.0"`; superfície sancionada = o
`__all__` do pacote (16 símbolos), dividida em:

| Subcontrato | Símbolos sancionados |
| --- | --- |
| **Observabilidade** (fronteira transversal, target sec. 3.5) | ExecutionMonitor, ExecutionReport, ExecutionSnapshot, ExecutionStatus, MonitorSnapshot, ScheduleOutcome, SchedulerReport, StepOutcome, StepRunner, StepStatus |
| **Governação** (agendamento e filas) | MultilayerExecutionQueue, QueueItem, QueueSnapshot, RuntimeManager, Scheduler, priority_for_plan |

A observabilidade mapeia os critérios progressivos do target:
duração (`ExecutionSnapshot.elapsed`, `started_at`), estado (`running`,
`current_step`, `ExecutionStatus`, `StepStatus`), falhas/timeouts
(reportes), estratégia seleccionada (`SchedulerReport`), agendamento
(`ScheduleOutcome`), e reserva o enriquecimento futuro (CPU/RAM/VRAM,
modelo/provider, addon, projecto) sem alterar a superfície.

## Implementação pesada (não desce agora — KERNEL-08/09)

Permaneceram internas e **fora da superfície**: a maquinaria de colecção do
monitor (`_RunState`, trinco, relógio injectável, contadores, retenção de
reportes) em `runtime_engine/monitoring.py`, e os mecanismos de
agendamento/filas (`manager`, `scheduler`, `queue`). O KERNEL-08/09 move
essa mecânica para infra-estrutura por trás dos contratos públicos, sem
remover nenhum símbolo aqui versionado.

## Regra de fronteira (consumidores futuros)

Qualquer consumidor de `wsai2.runtime_engine` em `src` importa apenas ao
nível do pacote (`from wsai2.runtime_engine import …`), nunca módulos
internos. Hoje não existem consumidores; a regra fica pronta a proteger a
futura integração (API/UI/orquestração, KERNEL-10).

## Detecção automática

Extensão de `tests/test_boundary_kernel.py`:

- `runtime_engine` entra nas superfícies públicas congeladas (versão
  major.minor; `__all__` == 16 símbolos sancionados).
- `test_subcontrato_de_observabilidade` (novo) — a fronteira de
  observabilidade (10) + governação (6) partem exactamente a superfície;
  disjuntas.
- A regra de consumidores ao nível do pacote passa a cobrir o
  `runtime_engine`.

## Validação

```text
py -3.12 -m pytest
tests=501  failures=0  errors=0  skipped=0
```

(501 = 500 + 1 teste do subcontrato; zero arestas novas; `FIREWALL` e
aciclicidade intactos.)

## Próximo passo

`/wsai-plan KERNEL-07` — Architecture contract tests (consolidação dos
contratos de fronteira já criados).