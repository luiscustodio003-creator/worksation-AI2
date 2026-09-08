# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 9 — Knowledge Engine (subsistema 3.9) — EM CURSO**

## Estado da fase

**FASE 9 INICIADA** após o fecho formal da Fase 8 (gate de fundação `APPROVED WITH WARNINGS`). A unidade 9.1 — **Knowledge Contract** — está concluída: contrato declarativo e imutável do subsistema (`wsai2.knowledge`), autorizando `knowledge` no teste de contrato arquitectural. A decisão de fronteira foi documentada (subsistema folha, sem arestas novas em `FRONTEIRAS`). Suíte completa: **433 testes aprovados, 0 falhas**.

## Última unidade implementada

Fase 9 — unidade 9.1: **Knowledge Contract** (`docs/knowledge/BASE-37-knowledge-engine-contract.md`). Criado `wsai2.knowledge` com `KnowledgeKind` (document/extract/note), `KnowledgeMetadata` (fonte, idioma, autor, etiquetas, extras), `KnowledgeRecord` (frozen, validado à criação) e `KNOWLEDGE_CONTRACT_VERSION = "1.0"`. Subsistema folha (só stdlib). O teste de contrato arquitectural passou a autorizar `knowledge` (fica `SUBSISTEMAS_FUTUROS = ("api", "ui")`). 10 novos testes.

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

Foram adicionados **10 testes** em `tests/test_knowledge.py`, cobrindo o contrato do Knowledge Engine (construção, validação à criação, imutabilidade, defaults, enums e resumo textual). A execução registou **433/433 testes aprovados**.

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
Knowledge Engine       █░░░░░░░░░ 10%  (contrato 9.1 — em curso)
API                    ░░░░░░░░░░ 0%   (não iniciado)
UI                     ░░░░░░░░░░ 0%   (não iniciado)
```

Estas barras não representam progresso global do projecto; representam maturidade/cobertura arquitectural de cada área. A conclusão de uma fase é determinada pelo estado e pelos gates, não pela soma das percentagens.

## Estado Git

A unidade 9.1 (contrato do Knowledge Engine) foi registada em `main` num commit coerente: módulo `knowledge` (base + init), testes, BASE-37 e documentação arquitectural/estado alinhados.

## Regra de continuação

**Fase 9 — Knowledge Engine EM CURSO.** A próxima unidade é a **9.2 — registo de conhecimento (ingestão/admissão)**:

```text
9.1 contrato do subsistema ✓ (esta unidade)
    ↓
9.2 KnowledgeRegistry — registo central de KnowledgeRecord
   (admissão por id, duplicações rejeitadas, padrão dos registos
    das Fases 4–8)
    ↓
9.3 extracção / metadados
9.4 indexação
9.5 recuperação
9.6 construção de contexto
```

A unidade 9.2 segue o padrão já autorizado dos `Registry` das Fases 4, 5,
6 e 8 (sem decisão arquitectural material nova) e pode ser executada de
forma autónoma. As unidades de indexação/recuperação (9.4/9.5) e a
estratégia de armazenamento exigirão decisão documentada antes de I/O;
essas decisões serão tratadas no devido ritmo, uma unidade de cada vez,
mantendo sempre a reversibilidade.

Nenhum I/O, motor de embeddings ou armazenamento persistente é criado
antes dessa decisão.
