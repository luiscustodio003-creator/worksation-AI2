# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Estado actual

**KERNEL CONSOLIDADO / FROZEN** — a migração KERNEL-01..KERNEL-10 e o fecho de consolidação estão concluídos. O desenvolvimento normal não reabre o Kernel para novas capacidades.

**API-01 CONCLUÍDA** — fundação contract-first com `ApiRequest`, `ApiResponse`, `ApiGateway`, `StdLibHttpGateway` e health.

**KNOWLEDGE 9.1–9.7 CONCLUÍDA (âmbito lexical)** — enriquecimento semântico permanece como decisão material terminal e não deve ser iniciado sem planeamento próprio.

**APP-06 CONCLUÍDA (Ramo A)** — use-case Capabilities resolvido: `CapabilitiesService` em `wsai2.application.capabilities_uc` constrói o `CapabilitiesResponse` via `build_compatibility` e honra o filtro `CapabilitiesRequest.domain`. Por decisão do utilizador, `wsai2.capability` passou a associar `domain` às definições (`CapabilityDefinition.domain`) e ganhou `CompatibilityReport.by_domain` — a lógica de agrupamento vive no domínio. Superfície de `wsai2.application` com 26 símbolos. Suíte **548/548 verdes** (541 + 3 domínio + 5 APP-06).

## Próximo ramo autorizado

**BRANCH A — APPLICATION / USE-CASE BOUNDARY**

Estado: **IN_PROGRESS** (APP-01..APP-06 congeladas)

Próxima unidade:

`APP-07 — Models`

Esta unidade deve resolver o use-case de avaliação/modelos (satisfazendo `ModelsRequest`/`ModelsResponse`), reutilizando `wsai2.model` e o filtro opcional por categoria.

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
- Application / Use Cases (Ramo A) — APP-01..06 concluídas (auditoria + contratos + System + Hardware + Runtime + Capabilities); APP-07+ pendentes.
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

`APP-06 — Capabilities` (Ramo A) — `CapabilitiesService` resolve o use-case de capacidades (`CapabilitiesRequest`/`CapabilitiesResponse`) via `build_compatibility`, com filtro por domínio (`CapabilityDefinition.domain` + `CompatibilityReport.by_domain` no módulo de domínio); suíte real confirmada: **548/548 verdes**.

`APP-05 — Runtime` (Ramo A) — `RuntimeProfileService` resolve o use-case de estado de runtime (`RuntimeProfileRequest`/`RuntimeProfileResponse`) via `discover_runtime`, com fonte injectável; suíte real confirmada: **541/541 verdes**.

`APP-04 — Hardware` (Ramo A) — `HardwareProfileService` resolve o use-case de perfil de hardware (`HardwareProfileRequest`/`HardwareProfileResponse`) via `discover_hardware`, com fonte injectável; suíte real confirmada: **537/537 verdes**.

`APP-03 — System / Platform` (Ramo A) — `SystemInfoService` resolve o use-case de informação do sistema (`SystemInfoRequest`/`SystemInfoResponse`) a partir das superfícies de `platform` e `runtime`, com fontes injectáveis; suíte real confirmada: **533/533 verdes**.

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
