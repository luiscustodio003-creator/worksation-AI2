# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 9 — Knowledge Engine (subsistema 3.9) — CONCLUÍDA (âmbito lexical)**

## Estado da fase

**FASE 9 CONCLUÍDA (âmbito lexical)** — fecho formal após gate `/wsai-validate fase9` (`APPROVED`, 2026-09-09, `docs/validation/FASE9_VALIDATION_REPORT.md`). Unidades **9.1 – 9.7** implementadas, testadas e sincronizadas: contrato → registo → metadados → índice → persistência → contexto → ingestão de ficheiros. Decisões documentadas (`knowledge` autorizado; aresta `knowledge→core`; 9.4 memória pura; 9.5 SQLite local). Suíte completa: **491 testes aprovados, 0 falhas**. O enriquecimento semântico (embeddings) é a **decisão material terminal** — permanece em aberto por natureza e fica registado como próximo ponto.

## Última unidade implementada

KERNEL-10 — **Contrato de addon** (`docs/architecture/KERNEL-10-addon-contract-freeze.md`). Superfície de `wsai2.extension` congelada por teste (10 símbolos) + `EXTENSION_CONTRACT_VERSION = "1.0"` (fora do `__all__`) + guarda de consumidores ao nível do pacote. `extension` continua fora de `KERNEL_SUBSISTEMAS` (camada addon). Sem novo subsistema SDK e sem código de Projects (decisão do plano; Projects = addon futuro do alvo, sec. 9). Suíte **506/506 verdes**.

## Estado dos residuais Via B

- Residual 1 — monitorização contínua: **CONCLUÍDO** (`BASE-34`).
- Residual 2 — concorrência entre planos: **CONCLUÍDO** (`BASE-35`).
- Residual 3 — filas multicamadas: **CONCLUÍDO** (`BASE-36`).

## Subsistemas funcionais implementados

- Platform Foundation
- Hardware Intelligence
- Runtime Intelligence
- Capability Engine
- Model Intelligence
- Provider Layer
- Task Intelligence
- Extension Contract
- Execution Context + Error Model
- Resource Governance
- Runtime Engine
- Monitorização contínua do Runtime
- Concorrência entre planos
- Filas multicamadas do Runtime: prioridade + backlog + preempção de pendentes
- Extension Lifecycle + Compatibility
- Architecture Contract Tests
- Security / Policy + Project Isolation
- Gate — Core pronto para addons
- Knowledge Contract (Fase 9, subsistema 3.9 — contrato declarativo)
- Knowledge Registry (Fase 9, subsistema 3.9 — admissão por id único)
- Knowledge Metadata Extraction (Fase 9, subsistema 3.9 — idioma/etiquetas/proveniência)
- Knowledge In-Memory Index (Fase 9, subsistema 3.9 — consulta por termos)
- Knowledge SQLite Persistence (Fase 9, subsistema 3.9 — armazenamento local decidido)
- Knowledge Context Builder (Fase 9, subsistema 3.9 — pacote de contexto determinista)
- Knowledge File Ingestion (Fase 9, subsistema 3.9 — ficheiros de texto do projecto)

## Filas multicamadas — contrato

`MultilayerExecutionQueue` é genérica e thread-safe. A prioridade é determinada por `ExecutionPriority` (`CRITICAL`, `HIGH`, `NORMAL`, `LOW`). Com `max_ready=None`, a camada pronta funciona como priority queue. Com capacidade limitada, uma entrada superior pode preemptar a menor prioridade ainda pronta, que passa para o backlog. Nenhum trabalho já iniciado é interrompido.

O Scheduler aceita `queue=None` por omissão. Quando uma fila é fornecida, os planos são admitidos e consumidos pela mesma pipeline de execução, mantendo políticas, monitorização, timeout, recovery, `step_runner` e concorrência existentes.

## Desenvolvimento controlado

A família oficial de comandos OpenCode é:

- `/wsai`
- `/wsai-run`
- `/wsai-audit`
- `/wsai-plan`
- `/wsai-implement`
- `/wsai-test`
- `/wsai-validate`
- `/wsai-doc`
- `/wsai-git`

Regra: a arquitectura real do código e testes é a fonte primária; documentação declara intenção/estado mas não substitui execução de testes.

## Validação da fundação

### Evidência actual

Execução real da suíte completa no fecho formal (2026-09-09):

- **423 testes passed / 0 failed / 0 errors / 0 skipped** (junitxml, `exit 0`);
- Python 3.12 / Windows;
- 10/10 testes de contrato arquitectural aprovados;
- invariantes das filas multicamadas aprovadas;
- gate `/wsai-validate foundation`: **🟡 APPROVED WITH WARNINGS**;
- nenhum blocker funcional ou arquitectural.

### GAPs identificados e tratamento

- **FV-01 — P2 — RESOLVIDO:** `ARCHITECTURE.md` e `CORE_HARDENING_PLAN.md` mantinham as filas multicamadas como futuras. Foram alinhados com a implementação real, BASE-36 e PROJECT_STATE.
- **FV-02 — P3 — ABERTO:** execução remota do GitHub Actions ainda não foi confirmada. Existe workflow `.github/workflows/tests.yml`; o estado remoto deve ser confirmado quando a API das Actions disponibilizar a execução.
- **FV-03 — P3 — RESOLVIDO DOCUMENTALMENTE:** `ARCHITECTURE.md` esclarece que as percentagens são indicadores de maturidade/cobertura arquitectural, não percentagens de implementação da fase.
- **FV-04 — P3 — NÃO BLOQUEANTE:** duplicação interna da ordem de prioridades e superfície pública `priority_for_plan` ficam como melhoria futura de baixo risco; não justificam alterar a arquitectura nem reabrir a Fase 8.
- **W-01 — P2 — RESOLVIDO NESTE GATE:** relatório persistente truncado e `PROJECT_STATE.md` sem fecho; resolvido como unidade correctiva documental do próprio gate, sem alteração de código funcional.

A documentação está alinhada com o estado funcional conhecido. A Fase 8 está **formalmente encerrada**.

## Testes

Baseline do fecho da Fase 8: **423 testes**.

Foram adicionados **10 testes** em `tests/test_knowledge.py` (contrato 9.1), **8 testes** em `tests/test_knowledge_registry.py` (registo 9.2), **14 testes** em `tests/test_knowledge_metadata.py` (extracção 9.3), **11 testes** em `tests/test_knowledge_index.py` (índice 9.4), **8 testes** em `tests/test_knowledge_storage.py` (persistência 9.5), **8 testes** em `tests/test_knowledge_context.py` (contexto 9.6) e **9 testes** em `tests/test_knowledge_ingest.py` (ingestão 9.7). A execução registou **491/491 testes aprovados**.

Foi também criado `.github/workflows/tests.yml` para executar a suíte em Python 3.12 no GitHub Actions. O estado remoto continua tratado como evidência P3 até existir confirmação de uma execução.

## Estado da arquitectura

```text
Foundation             ████████░░ 80%  (maturidade/cobertura)
Platform               ████████░░ 80%  (maturidade/cobertura)
Hardware Intelligence  ██████████ 100%
Runtime Intelligence   ██████████ 100%
Capability Engine      ██████████ 100%
Model Intelligence     ██████████ 100%
Provider Layer         ██████████ 100%
Task Intelligence      ██████████ 100%
Runtime Engine         ██████████ 100% (implementação)
Knowledge Engine       ███████░░░ 70%  (9.1–9.7 lexical completo; embeddings em decisão)
API                    ░░░░░░░░░░ 0%   (não iniciado)
UI                     ░░░░░░░░░░ 0%   (não iniciado)
```

Estas barras não representam progresso global do projecto; representam maturidade/cobertura arquitectural de cada área. A conclusão de uma fase é determinada pelo estado e pelos gates, não pela soma das percentagens.

## Migração do Kernel (Core / Execution & Intelligence Kernel)

**Estado arquitectura: CONSOLIDADO** (`docs/architecture/CORE_KERNEL_TARGET.md`
e `docs/validation/KERNEL_CONSOLIDATION_REPORT.md` vigentes;
`COMMAND_EXECUTION_CONTRACT.md` governou a transição, concluída).

- **KERNEL-01 — CORE INVENTORY: CONCLUÍDA** (`docs/architecture/KERNEL-01-core-inventory.md`). Auditoria read-only: 79 módulos / 14 subsistemas; Kernel = `core`/`execution`/`resource`/`runtime_engine`/`security`; domínio = `hardware`/`runtime`/`capability`/`model`/`provider`/`task`/`knowledge`; infra = `platform`; addon = `extension`; sem Application. 22 arestas `FRONTEIRAS` válidas, grafo acíclico, **491/491 testes verdes**. Sem código alterado.
- **KERNEL-02 — MAPA DE DEPENDÊNCIAS: CONCLUÍDA** (`docs/architecture/KERNEL-02-dependency-map.md`). Mapa formal (22 arestas, consumidores reais por scan AST) + candidata a `core.public` (símbolos públicos reais do núcleo). Documental, sem código alterado; decisão do conjunto definitivo fica no KERNEL-03.
- **KERNEL-03 — CORE PUBLIC CONTRACT: CONCLUÍDA** (`docs/architecture/KERNEL-03-core-public-contract.md`). Criado `wsai2.core.public` (Opção A): fachada versionada (`CORE_PUBLIC_CONTRACT_VERSION = "1.0"`) dos 14 símbolos do leaf `core` (erros + contexto), sem lógica própria nem novas arestas — `core` permanece folha. Bloqueio de localização resolvido em planeamento (agregado único violaria aciclicidade). 5 testes novos (`test_core_public.py`). Suíte **496/496 verdes**.
- **KERNEL-04 — DEPENDENCY FIREWALL: CONCLUÍDA** (`docs/architecture/KERNEL-04-dependency-firewall.md`). Firewall exacto por subsistema (`FIREWALL`, 26 arestas com tipagem) + teste automático `test_artigo2_13_firewall_por_subsistema` que detecta qualquer aresta nova; `core` permanece folha; grandfathering dos imports internos até KERNEL-08. Sem MOVE físico. Suíte **497/497 verdes**.
- **KERNEL-05 — RESOURCE / EXECUTION BOUNDARY: CONCLUÍDA** (`docs/architecture/KERNEL-05-execution-resource-boundary.md`). Opção A: fronteira = `__all__` do `__init__` de `execution`/`resource`/`security` + `EXECUTION_CONTRACT_VERSION`/`RESOURCE_CONTRACT_VERSION`/`SECURITY_CONTRACT_VERSION = "1.0"`; `tests/test_boundary_kernel.py` (3 testes: versão major.minor, superfícies congeladas, consumidores só ao nível do pacote). Sem fachadas novas e sem MOVE. `runtime_engine` fica para o KERNEL-06. Suíte **500/500 verdes**.
- **KERNEL-06 — OBSERVABILITY BOUNDARY: CONCLUÍDA** (`docs/architecture/KERNEL-06-observability-boundary.md`). `RUNTIME_ENGINE_CONTRACT_VERSION = "1.0"`; superfície sancionada (16 símbolos) congelada e partida em observabilidade (10) vs governação (6); `test_subcontrato_de_observabilidade` novo; regra de consumidores ao nível do pacote alargada ao `runtime_engine`. Implementação pesada (colecção de métricas) permanece interna → KERNEL-08/09. Suíte **501/501 verdes**.
- **KERNEL-07 — ARCHITECTURE CONTRACT TESTS: CONCLUÍDA** (`docs/architecture/KERNEL-07-architecture-contract-tests.md`). Fonte única de verdade `tests/architecture_contracts.py` (FRONTEIRAS, FIREWALL, superfícies, versões) + refactor dos 3 ficheiros de contrato (literais removidos) + `test_kernel_todas_as_superficies_publicas_versionadas` (os 5 subsistemas do kernel com superfície versionada; bumps deliberados detectados). Sem alteração de `src`. Suíte **502/502 verdes**.
- **KERNEL-08 — IMPORT MIGRATION (via core.public): CONCLUÍDA** (`docs/architecture/KERNEL-08-import-migration-core-public.md`). Opção A do plano: os 13 consumidores migram de `wsai2.core.{errors,context}` para `wsai2.core.public` (mesmos objectos; zero arestas novas) + regra de contrato `test_consumidores_core_apenas_via_public` (scan AST: fora de `core`, só `core.public`). Descida física da implementação pesada fica como decisão em aberto. Suíte **503/503 verdes**.
- **KERNEL-09 — CORE FREEZE (implementação pesada fora do núcleo): CONCLUÍDA** (`docs/architecture/KERNEL-09-core-freeze-heavy-descend.md`). Descida completa (opção B do plano KERNEL-08, confirmada): novo subsistema `wsai2.infrastructure` (7 módulos: base_resource, governor, base_runtime, manager, scheduler, queue, monitoring) recolhe a mecânica pesada; `resource`/`runtime_engine` viram shells de re-export (superfícies e versões intactas; `git mv` com histórico). Fronteiras recompostas (26 arestas: `resource→infrastructure`, `runtime_engine→infrastructure`, `infrastructure→{core,execution,extension,hardware,runtime,security,task}`); `execution`/`security` ficam no núcleo (ciclo `execution⇄infra` bloqueia o runner). Guarda nova `test_implementacao_pesada_fora_do_nucleo` + BASE-44 + excepção de shell nos placeholders. Suíte **504/504 verdes**.
- **KERNEL-10 — CONTRATO DE ADDON: CONCLUÍDA** (`docs/architecture/KERNEL-10-addon-contract-freeze.md`). Superfície de `wsai2.extension` congelada por teste (10 símbolos) + `EXTENSION_CONTRACT_VERSION = "1.0"` (fora do `__all__`) + `test_consumidores_extension_apenas_nivel_pacote`. `extension` permanece fora de `KERNEL_SUBSISTEMAS` (camada addon, tabelas `ADDON_CONTRATO_*` na fonte única). Decisão de âmbito do plano: sem novo subsistema SDK (duplicação) e sem código de Projects (addon futuro do alvo, sec. 9 — só documental). Sem arestas novas. Suíte **506/506 verdes**; sequência KERNEL-01..KERNEL-10 **concluída**.
- **KERNEL-CONSOLIDATION-CLOSE: CONCLUÍDA** (`docs/validation/KERNEL_CONSOLIDATION_REPORT.md`). Fecho formal da transição: sequência KERNEL-01..10 consolidada em `main` por *fast-forward* (sem conflitos), com gate **506/506** e documentação persistente do marco. Nenhum código funcional alterado (unidade de processo/estado). O kernel deixa o estado TRANSITION e passa a CONSOLIDADO.
- **Próxima decisão (material, a planeamento próprio):** Fase 10 — API (framework HTTP) ou addon Projects (primeiro consumidor real do contrato de addon); Fase 9 embeddings continua registada como decisão material terminal.
- **Política de reconstrução do Core (regra de superfície vs. implementação):** registada em `CORE_KERNEL_TARGET.md` (sec. 2, 6, 10, 11, 12) e `COMMAND_EXECUTION_CONTRACT.md` (regras de migração): a reconstrução nunca remove superfícies públicas já versionadas; a implementação pesada (mecânica de execução) foi extraída do núcleo para `wsai2.infrastructure`, por trás dos contratos públicos, no KERNEL-09.

## Estado Git

As unidades 9.1–9.7 (contrato, registo, extracção, índice, persistência,
contexto e ingestão de conhecimento) foram registadas em `main` em
commits coerentes: módulo `knowledge` (base, init, registry, metadata,
index, storage, context, ingest), testes, BASE-37/38/39/40/41/42/43 e
documentação arquitectural/estado alinhados.

No KERNEL-CONSOLIDATION-CLOSE (2026-09-10), a sequência KERNEL-01..KERNEL-10
(commits `d74e55d..7f0b2aa` em `core-hardening-foundation`) foi consolidada
em `main` por *fast-forward* sem conflitos, com gate **506/506** — o kernel
deixa o estado TRANSITION e fica CONSOLIDADO.

## Regra de continuação

**Migração do Kernel — CONSOLIDADO (KERNEL-01 a KERNEL-10 concluídas; fecho da transição).**

```text
KERNEL-01  Inventário real da base            ✓ CONCLUÍDA (auditoria read-only)
KERNEL-02  Mapa de dependências + core.public ✓ CONCLUÍDA (documental; candidata registada)
KERNEL-03  Core Public Contract               ✓ CONCLUÍDA (core.public; Opção A, 496/496)
KERNEL-04  Dependency Firewall                ✓ CONCLUÍDA (FIREWALL por subsistema; 497/497)
KERNEL-05  Resource / Execution boundary      ✓ CONCLUÍDA (Opção A; fronteiras versionadas; 500/500)
KERNEL-06  Observability boundary             ✓ CONCLUÍDA (fronteira de observabilidade; 501/501)
KERNEL-07  Architecture contract tests        ✓ CONCLUÍDA (fonte única de contratos; 502/502)
KERNEL-08  Migração incremental de imports    ✓ CONCLUÍDA (consumidores só via core.public; 503/503)
KERNEL-09  Core freeze                        ✓ CONCLUÍDA (implementação pesada em wsai2.infrastructure; 504/504)
KERNEL-10  Contrato de addon                  ✓ CONCLUÍDA (extension congelada e versionada; 506/506)
SEQUÊNCIA KERNEL-01..KERNEL-10                ✓ CONCLUÍDA — contrato de addon pronto para consumidores
```

O fecho da Fase 9 e a linha do Kernel coexistem: a migração não reverterá
a ingestão 9.7 nem o fecho formal.

**Fase 9 — Knowledge Engine — CONCLUÍDA (âmbito lexical, fecho formal em 2026-09-09).**

```text
9.1 contrato do subsistema ✓
9.2 registo central — Knowledge Registry ✓
9.3 extracção de metadados (heurística) ✓
9.4 indexação — Knowledge In-Memory Index ✓ (decisão: memória pura)
9.5 recuperação — Knowledge SQLite Persistence ✓ (decisão: SQLite local)
9.6 construção de contexto ✓
9.7 ingestão de ficheiros de texto do projecto ✓ (lexical — sem embeddings)
    ↓
FECHO FORMAL da Fase 9 (âmbito lexical) ✓ — gate APPROVED
    ↓
ENRIQUECIMENTO SEMÂNTICO — embeddings via Model/Provider — DECISÃO
MATERIAL TERMINAL: decisões de modelo/fornecedor, integração Provider/
Runtime e aditividade sobre o índice léxico. Planeamento próprio.
    ↓
Fase 10 — API (health/system/hardware/runtime/capabilities/models/tasks/
knowledge) — requer decidir framework HTTP.
```

O **âmbito lexical da Fase 9 está completo e sincronizado**. O próximo
ponto é a **decisão material terminal** sobre embeddings (modelo,
fornecedor e integração com Provider/Runtime) — a tratar numa sessão de
planeamento própria antes de qualquer motor de embeddings. Nenhum recurso
desse âmbito é criado antes dessa decisão.
