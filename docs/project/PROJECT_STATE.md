# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Estado actual

**KERNEL CONSOLIDADO / FROZEN** — a migração KERNEL-01..KERNEL-10 e o fecho de consolidação estão concluídos. O desenvolvimento normal não reabre o Kernel para novas capacidades.

**API-01 CONCLUÍDA** — fundação contract-first com `ApiRequest`, `ApiResponse`, `ApiGateway`, `StdLibHttpGateway` e health.

**KNOWLEDGE 9.1–9.7 CONCLUÍDA (âmbito lexical)** — enriquecimento semântico permanece como decisão material terminal e não deve ser iniciado sem planeamento próprio.

**APP-02 CONCLUÍDA (Ramo A)** — contratos de use-case definidos e sancionados: subsistema `wsai2.application` com 20 mensagens puras de pedido/resposta por área (system/platform, hardware, runtime, capabilities, models, tasks, knowledge, execution/status/cancelamento), `APPLICATION_CONTRACT_VERSION = "1.0"`, fronteiras `application → {capability, core, hardware, knowledge, model, platform, runtime, runtime_engine, task}` autorizadas na fonte única. A Application reutiliza as superfícies públicas de domínio (REUSE) e não contém lógica central de negócio. Suíte **528/528 verdes** (513 + 15 novos).

## Próximo ramo autorizado

**BRANCH A — APPLICATION / USE-CASE BOUNDARY**

Estado: **IN_PROGRESS** (APP-01, APP-02 congeladas)

Próxima unidade:

`APP-03 — System / Platform`

Esta unidade deve implementar o adaptador do use-case de informação do sistema (satisfazendo `SystemInfoRequest`/`SystemInfoResponse`), reutilizando `wsai2.platform` e `wsai2.runtime` e integrando os serviços de domínio já existentes.

## Governação do /wsai-run

As regras persistentes estão em `docs/project/RUN_GOVERNANCE.md`.

O `/wsai-run` trabalha por ramos e unidades:

```text
AUDIT → PLAN → ARQ → IMPLEMENT → TEST → VALIDATE → DOC → GIT → FREEZE
```

Depois de cada unidade concluída, o estado deve ser persistido e a próxima unidade determinada. Se estiver pronta, o Run continua. Se estiver bloqueada, o Run para e guarda o ponto exacto.

Quando todas as unidades de um ramo terminarem sem erros, o ramo passa a `COMPLETE / FROZEN`. Antes de iniciar outro ramo, o Run verifica dependências e gates reais.

## Estado persistente mínimo do Run

```text
active_branch
branch_status
active_unit
unit_status
current_step
last_completed_step
next_action
blocked_reason
dependencies_checked
frozen_units
frozen_branches
last_commit
```

## Ramos planeados pós-Kernel

```text
A — APPLICATION / USE CASES       READY
B — API / DOMAIN RESOURCES        DEPENDENT ON APPLICATION
C — UI                            DEPENDENT ON API / APPLICATION
D — KNOWLEDGE SEMANTIC            MATERIAL DECISION / OWN GATE
E — ADDON ECOSYSTEM               DEPENDS ON PUBLIC CONTRACTS
F — PROJECTS ADDON                ADDON / DEPENDENCY GATE
```

Os ramos são um mapa operacional e não uma autorização para criar todas as unidades antecipadamente. O código e os testes existentes devem ser auditados antes de cada unidade.

## Estado das fases funcionais

- Platform Foundation — implementada.
- Hardware Intelligence — implementada.
- Runtime Intelligence — implementada.
- Capability Engine — implementada.
- Model Intelligence — implementada.
- Provider Layer — implementada.
- Task Intelligence — implementada.
- Runtime Engine — implementada e fechada.
- Knowledge Engine — fechada no âmbito lexical (9.1–9.7).
- Application / Use Cases (Ramo A) — APP-01/02 concluídas (auditoria + contratos); APP-03+ pendentes.
- API — API-01 concluída; API-02+ pendentes.
- UI — ainda não iniciada.

## Política de reutilização

Antes de criar uma responsabilidade nova:

```text
REUSE → ADAPT → WRAP/ADAPTER → EXTEND → CREATE
```

A existência de um símbolo, serviço, adapter ou contrato semelhante deve ser verificada no código e nos testes. Documentação futura não conta como implementação existente.

## Fecho do Kernel

KERNEL-01..KERNEL-10: **CONCLUÍDOS**.

`docs/validation/KERNEL_CONSOLIDATION_REPORT.md` é a evidência persistente do fecho. O estado `TRANSITION` do Kernel terminou; qualquer futura reabertura deve ser controlada e justificada por BUG, REGRESSION, SECURITY, CONTRACT VIOLATION, REQUIREMENT CHANGE ou outra falha real que torne o estado incorrecto.

## Última unidade funcional

`APP-02 — Use-Case Contracts` (Ramo A) — contratos de use-case da camada Application (`wsai2.application`, 20 mensagens), fronteira sancionada e `PlatformInfo` exposto na superfície `wsai2.platform`; suíte real confirmada: **528/528 verdes**.

`APP-01 — Audit Application Boundary` (Ramo A) — auditoria read-only da fronteira Application; suíte real confirmada: **513/513 verdes**.

`API-01 — Fundação do subsistema API` — suíte registada no fecho: **513/513 verdes**.

## Testes e validação

As contagens históricas acima são evidência do momento em que cada gate foi fechado. O estado actual deve ser confirmado executando a suíte real antes de cada novo gate estrutural.

## Fonte de verdade

A decisão operacional deve cruzar:

1. código real;
2. testes;
3. `PROJECT_STATE.md`;
4. `ROADMAP.md`;
5. arquitectura/constituição;
6. `RUN_GOVERNANCE.md`;
7. Git.
