# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 9 — Knowledge Engine (subsistema 3.9) — EM CURSO**

## Estado da fase

**FASE 9 INICIADA** após o fecho formal da Fase 8 (gate de fundação `APPROVED WITH WARNINGS`). Unidades **9.1 — Knowledge Contract**, **9.2 — Knowledge Registry**, **9.3 — Metadata Extraction**, **9.4 — In-Memory Index** e **9.5 — SQLite Persistence** concluídas: contrato declarativo e imutável (`wsai2.knowledge`), registo central de admissão por id único (padrão dos registos F4–8), extracção heurística de metadados, índice invertido em memória e persistência SQLite (decisões 9.4/9.5 documentadas). Decisões de fronteira documentadas (`knowledge` autorizado; aresta `knowledge→core`). Suíte completa: **474 testes aprovados, 0 falhas**.

## Última unidade implementada

Fase 9 — unidade 9.5: **Knowledge SQLite Persistence** (`docs/knowledge/BASE-41-knowledge-sqlite-persistence.md`). Criado `KnowledgeStore` (persistência local por id com esquema `knowledge_record`, metadados serializados em JSON, `save`/`save_all`/`delete`/`count`/`load` ordenada por id). **Decisão da unidade (consultada): persistência SQLite local** como estratégia de armazenamento da recuperação; embeddings continuam fora desta unidade. Sem arestas novas em `FRONTEIRAS`. 8 novos testes.

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

Foram adicionados **10 testes** em `tests/test_knowledge.py` (contrato 9.1), **8 testes** em `tests/test_knowledge_registry.py` (registo 9.2), **14 testes** em `tests/test_knowledge_metadata.py` (extracção 9.3), **11 testes** em `tests/test_knowledge_index.py` (índice 9.4) e **8 testes** em `tests/test_knowledge_storage.py` (persistência 9.5). A execução registou **474/474 testes aprovados**.

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
Knowledge Engine       █████░░░░░ 50%  (9.1–9.5: contrato, registo, metadados, índice, SQLite)
API                    ░░░░░░░░░░ 0%   (não iniciado)
UI                     ░░░░░░░░░░ 0%   (não iniciado)
```

Estas barras não representam progresso global do projecto; representam maturidade/cobertura arquitectural de cada área. A conclusão de uma fase é determinada pelo estado e pelos gates, não pela soma das percentagens.

## Estado Git

As unidades 9.1–9.5 (contrato, registo, extracção de metadados, índice e
persistência de conhecimento) foram registadas em `main` em commits
coerentes: módulo `knowledge` (base, init, registry, metadata, index,
storage), testes, BASE-37/38/39/40/41 e documentação arquitectural/estado
alinhados.

## Regra de continuação

**Fase 9 — Knowledge Engine EM CURSO.** As unidades **9.2 — Knowledge
Registry**, **9.3 — Metadata Extraction**, **9.4 — In-Memory Index** e
**9.5 — SQLite Persistence** foram executadas (padrão autorizado;
decisões 9.4 e 9.5 consultadas e documentadas).

```text
9.1 contrato do subsistema ✓
9.2 registo central — Knowledge Registry ✓
9.3 extracção de metadados (heurística) ✓
9.4 indexação — Knowledge In-Memory Index ✓ (decisão: memória pura)
9.5 recuperação — Knowledge SQLite Persistence ✓ (decisão: SQLite local)
    ↓
9.6 construção de contexto — montagem textual determinista a partir do
   índice (9.4) e dos registos persistidos (9.5) — sem decisão material
9.7/rolo seguinte — ingestão e extracção semântica real (ficheiros de
   projecto, embeddings via Model/Provider) — exige planeamento próprio
   e decisões documentadas; sessão dedicada.
```

A unidade **9.6 — construção de contexto** é executável de forma autónoma
na mesma sessão caso o `/wsai-run` continue (unidade pura e directamente
dependente). A **ingestão semântica real** (ficheiros/embeddings) é o
ponto de paragem seguinte e exige planeamento próprio. Nenhum motor de
embeddings é criado antes dessa decisão.
