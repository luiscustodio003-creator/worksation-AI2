# WSAI2 — RUN STATE

## Estado global

```text
PROJECT_STATUS: ACTIVE
KERNEL_STATUS: FROZEN
ACTIVE_BRANCH: A — APPLICATION / USE CASES
BRANCH_STATUS: IN_PROGRESS
ACTIVE_UNIT: APP-10
UNIT_STATUS: PENDING
CURRENT_STEP: AUDIT
NEXT_ACTION: Execution/Status/Cancellation use-cases
BLOCKED_REASON: NONE
```

## Branches

| Ramo | Estado | Dependência | Próximo passo |
|---|---|---|---|
| A — Application / Use Cases | IN_PROGRESS | Kernel frozen | APP-10 (APP-01..09 congeladas) |
| B — API | PENDING | Application | API-02 |
| C — UI | PENDING | API/Application | UI-01 |
| D — Knowledge Semantic | BLOCKED | decisão material própria | KNOW-SEM-01 |
| E — Addon Ecosystem | PENDING | contratos públicos | ADDON-01 |
| F — Projects Addon | PENDING | Addon/Application/Knowledge conforme unidade | PROJECT-01 |

## Unidade activa

```text
BRANCH: A
UNIT: APP-10
DESCRIPTION: Execution/Status/Cancellation use-cases
STEP: AUDIT
STATUS: PENDING
```

## Unidades congeladas (Ramo A)

```text
APP-01  Audit Application Boundary    COMPLETE / FROZEN
        Evidência: docs/application/APP-01-application-boundary-audit.md
APP-02  Use-Case Contracts            COMPLETE / FROZEN
        Evidência: docs/application/BASE-46-application-use-case-contracts.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-02)
APP-03  System / Platform             COMPLETE / FROZEN
        Evidência: docs/application/BASE-47-system-platform-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-03)
APP-04  Hardware                      COMPLETE / FROZEN
        Evidência: docs/application/BASE-48-hardware-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-04)
APP-05  Runtime                       COMPLETE / FROZEN
        Evidência: docs/application/BASE-49-runtime-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-05)
APP-06  Capabilities                  COMPLETE / FROZEN
        Evidência: docs/application/BASE-50-capabilities-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-06)
APP-07  Models                        COMPLETE / FROZEN
        Evidência: docs/application/BASE-51-models-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-07)
APP-08  Task Analysis                 COMPLETE / FROZEN
        Evidência: docs/application/BASE-52-task-analysis-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-08)
APP-09  Knowledge Context              COMPLETE / FROZEN
        Evidência: docs/application/BASE-53-knowledge-context-use-case.md
                + docs/project/IMPLEMENTATION_LOG.md (APP-09)
```

## Regra de retoma

Se uma execução terminar por bloqueio, conservar o ramo, unidade e etapa exactos. A próxima chamada a `/wsai-run` retoma o primeiro passo incompleto.

Se a unidade for concluída, marcar `COMPLETE / FROZEN`, guardar o commit e seleccionar a próxima unidade do ramo.

Quando a última unidade do ramo for concluída, marcar o ramo `COMPLETE / FROZEN` e executar o Dependency Gate antes de seleccionar o próximo ramo.

## Regras

- Não reabrir o Kernel para novas capacidades.
- Não reabrir unidades/ramos congelados automaticamente.
- Verificar dependências reais antes de mudar de ramo.
- Preferir `REUSE → ADAPT → WRAP/ADAPTER → EXTEND → CREATE`.
- Não considerar documentação futura como implementação existente.
- Não avançar perante decisão arquitectural material ou bloqueio técnico inseguro.
