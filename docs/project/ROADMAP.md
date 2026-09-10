# WORKSTATION AI 2 — ROADMAP DE DESENVOLVIMENTO

## Fase 0 — Fundação e Governação

- estrutura mínima do projecto;
- documentação arquitectural;
- regras globais;
- comando `/wsai-run`;
- família de comandos `/wsai-*` para execução individual das etapas;
- skill de desenvolvimento;
- política de modelos OpenCode;
- política Git;
- estado persistente;
- base de testes;
- ciclo controlado **AUDITAR → PLANEAR → IMPLEMENTAR → TESTAR → DOCUMENTAR → GIT**.

## Fase 1 — Platform Foundation

- detecção do sistema operativo;
- abstracção de plataforma;
- adaptadores Windows;
- adaptadores Linux;
- testes de compatibilidade.

## Fase 2 — Hardware Intelligence

- CPU;
- memória;
- GPU;
- armazenamento;
- perfil de hardware;
- capacidades estruturais.

## Fase 3 — Runtime Intelligence

- recursos disponíveis;
- carga;
- processos;
- estado de execução;
- perfil de runtime.

## Fase 4 — Capability Engine

- definições de capacidade;
- registo;
- avaliação;
- compatibilidade;
- capacidades disponíveis.

## Fase 5 — Model Intelligence

- registo de modelos;
- metadados;
- requisitos;
- compatibilidade;
- classificação;
- recomendação.

## Fase 6 — Provider Layer

- contratos de fornecedor;
- detecção;
- adaptadores de runtime;
- health checks.

## Fase 7 — Task Intelligence

- modelo de tarefa;
- classificação;
- extracção de requisitos;
- selecção de capacidades;
- plano de execução.

## Fase 8 — Runtime Engine

A Fase 8 começou pela **baseline e auditoria**, não por uma reescrita. O Runtime consome o `ExecutionPlan` já produzido pelo Task Intelligence.

### Preparação e hardening controlado

- auditoria da base existente;
- contratos mínimos de extensão quando necessários;
- modelo de erros transversal quando necessário;
- `ExecutionContext`;
- governação de recursos;
- timeout;
- cancelamento;
- recuperação;
- scheduler;
- gestor de execução;
- monitorização;
- lifecycle e compatibilidade;
- testes de contrato arquitectural;
- Security / Policy;
- Project Isolation;
- Gate — Core pronto para addons.

### Runtime funcional

- scheduler;
- gestor de execução;
- recursos;
- memória;
- cancelamento;
- timeout;
- monitorização;
- concorrência opcional entre planos;
- filas multicamadas com prioridade, backlog e preempção de trabalho pendente.

**Estado actual:** implementação funcional da Fase 8 concluída, incluindo os três residuais Via B. Gate de fundação executado com **APPROVED WITH WARNINGS** (2026-09-09). A Fase 8 está formalmente fechada.

## Fase 9 — Knowledge Engine

- contrato do subsistema (3.9) ✓ (9.1);
- registo central / admissão ✓ (9.2);
- extracção de metadados ✓ (9.3);
- indexação em memória ✓ (9.4);
- persistência SQLite ✓ (9.5);
- construção de contexto ✓ (9.6);
- ingestão de ficheiros de texto ✓ (9.7);
- enriquecimento semântico / embeddings — **decisão material terminal, planeamento próprio**;
- extracção;
- metadados;
- indexação;
- recuperação;
- contexto.

**Estado:** **CONCLUÍDA no âmbito lexical** — unidades 9.1–9.7 implementadas, testadas e sincronizadas. Embeddings permanecem fora da execução automática até existir decisão e plano próprios.

## Fase 10 — API

- health;
- system;
- hardware;
- runtime;
- capabilities;
- models;
- tasks;
- knowledge.

**Estado:** estratégia contract-first com transporte stdlib definida. **API-01 concluída**: contrato `API_CONTRACT_VERSION = "1.0"`, `ApiRequest`, `ApiResponse`, `ApiGateway`, `StdLibHttpGateway` e health. API-02+ permanecem por executar.

## Fase 11 — UI

- dashboard;
- hardware;
- modelos;
- capacidades;
- tarefas;
- runtime;
- conhecimento.

## Modelo pós-Kernel — ramos de desenvolvimento

O Kernel está consolidado e congelado. A partir deste ponto, o roadmap operacional passa a usar ramos controlados. Um ramo só é fechado depois de todas as suas unidades passarem pelo ciclo completo e serem congeladas.

```text
BRANCH A — APPLICATION / USE CASES
    APP-01  Audit Application Boundary           ✓ CONCLUÍDA (auditoria read-only)
    APP-02  Use-Case Contracts                    ✓ CONCLUÍDA (contratos + fronteira sancionada)
    APP-03  System / Platform                     ✓ CONCLUÍDA (SystemInfoService)
    APP-04  Hardware                              ✓ CONCLUÍDA (HardwareProfileService)
    APP-05  Runtime
    APP-06  Capabilities
    APP-07  Models
    APP-08  Tasks
    APP-09  Knowledge
    APP-10  Execution / Status / Cancellation
    APP-11  Application Integration Gate

BRANCH B — API
    API-02  System
    API-03  Hardware
    API-04  Runtime
    API-05  Capabilities
    API-06  Models
    API-07  Tasks
    API-08  Knowledge
    API-09  Execution / Status
    API-10  API Integration Gate

BRANCH C — UI
    UI-01  Application Shell
    UI-02  Dashboard
    UI-03  Hardware
    UI-04  Models
    UI-05  Capabilities
    UI-06  Tasks
    UI-07  Runtime
    UI-08  Knowledge
    UI-09  Execution / Status
    UI-10  UI Integration Gate

BRANCH D — KNOWLEDGE SEMANTIC
    KNOW-SEM-01  Architecture Decision
    KNOW-SEM-02  Model / Provider Design
    KNOW-SEM-03  Embedding Contract
    KNOW-SEM-04  Implementation
    KNOW-SEM-05  Persistence / Index Strategy
    KNOW-SEM-06  Validation Gate

BRANCH E — ADDON ECOSYSTEM
    ADDON-01  Discovery
    ADDON-02  Admission
    ADDON-03  Lifecycle
    ADDON-04  Compatibility
    ADDON-05  Permissions
    ADDON-06  Resource Requirements
    ADDON-07  Integration Gate

BRANCH F — PROJECTS ADDON
    PROJECT-01  Project Contract
    PROJECT-02  Project State / Isolation
    PROJECT-03  Project Knowledge Integration
    PROJECT-04  Skills / Commands Integration
    PROJECT-05  Project Integration Gate
```

Estas unidades são **mapa de trabalho**, não autorização para implementar tudo antecipadamente. Antes de cada unidade, o `/wsai-run` deve auditar o código real e reutilizar o que já existir.

## Dependências entre ramos

```text
APPLICATION ─────► API ─────► UI
     │
     ├────────────► PROJECTS
     │
     └────────────► ADDON ECOSYSTEM

KNOWLEDGE SEMANTIC ──► ADDONS/consumidores quando aplicável
```

A seta representa uma dependência impeditiva potencial, não uma ordem artificial. O `/wsai-run` deve confirmar a dependência real através dos contratos, gates e código antes de iniciar o ramo seguinte. Ramos sem dependência impeditiva podem avançar quando estiverem `READY`.

## Política de execução por ramo

Cada unidade segue:

```text
AUDIT → PLAN → ARQ → IMPLEMENT → TEST → VALIDATE → DOC → GIT → FREEZE
```

Depois da última unidade sem erros:

```text
BRANCH COMPLETE → BRANCH FROZEN → DEPENDENCY GATE → NEXT READY BRANCH
```

Se houver bloqueio:

```text
BLOCKED → SAVE STATE → STOP → REPORT NEXT ACTION
```

Uma nova chamada ao `/wsai-run` retoma do primeiro trabalho incompleto. Um ramo congelado não é reaberto automaticamente.

## Regra de transição entre fases

```text
ROADMAP — ramo/fase macro
      ↓
PROJECT_STATE — unidade concreta / estado real
      ↓
Código + testes + documentação
      ↓
Gate de validação aplicável
      ↓
BRANCH COMPLETE / FROZEN
      ↓
Dependency Gate
      ↓
próximo ramo READY
```

O roadmap define o mapa macro. O `PROJECT_STATE.md` e `RUN_GOVERNANCE.md` definem o estado operacional. A implementação real e os testes continuam a ser a fonte primária de evidência.
