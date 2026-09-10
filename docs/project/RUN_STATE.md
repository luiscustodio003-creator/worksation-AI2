# WSAI2 — RUN STATE

## Estado global

```text
PROJECT_STATUS: ACTIVE
KERNEL_STATUS: FROZEN
ACTIVE_BRANCH: A — APPLICATION / USE CASES
BRANCH_STATUS: IN_PROGRESS
ACTIVE_UNIT: APP-02
UNIT_STATUS: PENDING
CURRENT_STEP: AUDIT
NEXT_ACTION: Use-Case Contracts
BLOCKED_REASON: NONE
```

## Branches

| Ramo | Estado | Dependência | Próximo passo |
|---|---|---|---|
| A — Application / Use Cases | IN_PROGRESS | Kernel frozen | APP-02 (APP-01 audit congelada) |
| B — API | PENDING | Application | API-02 |
| C — UI | PENDING | API/Application | UI-01 |
| D — Knowledge Semantic | BLOCKED | decisão material própria | KNOW-SEM-01 |
| E — Addon Ecosystem | PENDING | contratos públicos | ADDON-01 |
| F — Projects Addon | PENDING | Addon/Application/Knowledge conforme unidade | PROJECT-01 |

## Unidade activa

```text
BRANCH: A
UNIT: APP-02
DESCRIPTION: Use-Case Contracts
STEP: AUDIT
STATUS: PENDING
```

## Unidades congeladas (Ramo A)

```text
APP-01  Audit Application Boundary    COMPLETE / FROZEN
        Evidência: docs/application/APP-01-application-boundary-audit.md
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
