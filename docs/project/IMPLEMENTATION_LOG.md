# WORKSTATION AI 2 — IMPLEMENTATION LOG

## 2026-09-09 — KERNEL-02 — Mapa de dependências e fronteiras públicas

### Objectivo

Fixar o mapa formal de dependências e a candidata a `core.public` para a
migração do Kernel (`TRANSITION`).

### Alterações

- `docs/architecture/KERNEL-02-dependency-map.md` — mapa (22 arestas,
  consumidores reais por scan AST) e superfície pública candidata
  (símbolos reais de `core`/`execution`/`resource`/`runtime_engine`/
  `security`); nós de atenção (`runtime_engine` concêntrico;
  `resource.governor→hardware` a reavaliar).
- `docs/project/PROJECT_STATE.md` — KERNEL-02 concluída; próxima unidade
  KERNEL-03 (Core Public Contract).
- Unidade documental — **sem código alterado**.

### Validação

```text
py -3.12 -m pytest
tests=491  failures=0  errors=0  skipped=0
```

### Próximo passo

`/wsai-plan KERNEL-03` — Core Public Contract (decisão do conjunto
definitivo de `core.public` e revisão de `resource.governor→hardware`).

## 2026-09-09 — KERNEL-01 — Inventário real da base

### Objectivo

Auditoria read-only do Kernel (`CORE INVENTORY`) antes de qualquer
reorganização, conforme a secção 12 do `CORE_KERNEL_TARGET.md`.

### Alterações

- `docs/architecture/KERNEL-01-core-inventory.md` — inventário de
  79 módulos / 14 subsistemas, classificação por destino arquitectural,
  22 arestas, mapa de consumidores reais, problemas (P3) e riscos de
  migração.
- `docs/project/PROJECT_STATE.md` — secção "Migração do Kernel" com o
  estado `TRANSITION`.
- Auditoria read-only — **sem código alterado**.

### Validação

```text
py -3.12 -m pytest
tests=491  failures=0  errors=0  skipped=0
```

### Próximo passo

`/wsai-plan KERNEL-02` (concluída em seguida).

## 2026-09-09 — Fecho formal da Fase 9 — validação do âmbito lexical

### Objectivo

Encerrar formalmente a Fase 9 — Knowledge Engine (subsistema 3.9) no
seu âmbito lexical (unidades 9.1–9.7), espelhando o gate da Fase 8.

### Alterações

- `docs/validation/FASE9_VALIDATION_REPORT.md` — relatório de validação
  com a estrutura oficial de 10 secções; resultado **APPROVED**
  (sem P0/P1/P2 bloqueantes; avisos P3 documentados).
- `docs/project/PROJECT_STATE.md` — `FASE 9 CONCLUÍDA (âmbito lexical)`;
  enriquecimento semântico (embeddings) registado como decisão material
  terminal; regra de continuação actualizada.
- `docs/project/ROADMAP.md` — estado da Fase 9 marcado como concluído
  (âmbito lexical).

### Validação

```text
py -3.12 -m pytest
tests=491  failures=0  errors=0  skipped=0
exit code: 0
```

### Próximo passo

Decisão material entre o enriquecimento semântico (embeddings via
Model/Provider) e a Fase 10 — API; integração da linha Kernel
(core-hardening-foundation) sobre a base completa.

## 2026-09-09 — Knowledge File Ingestion — Fase 9.7 (fecho do âmbito lexical)

### Objectivo

Ingerir os ficheiros de texto do projecto em registos do contrato 9.1
(tipo `document`) com proveniência relativa e metadados derivados,
fechando o âmbito **lexical** da Fase 9. Sem embeddings e sem decisão
arquitectural material.

### Realizado

- `src/wsai2/knowledge/ingest.py` (novo): `FileIngestor` — rglob sobre as
  extensões textuais suportadas, id por caminho relativo (`km.f.<path>`),
  `KnowledgeMetadataExtractor` (9.3) a derivar idioma/etiquetas,
  `limite_bytes`, binários/vazios/oversized ignorados, ordem determinista;
- `src/wsai2/knowledge/__init__.py` — exporta `FileIngestor`;
- `tests/test_knowledge_ingest.py` (novo, **9 testes**);
- `ARCHITECTURE.md` — secção 3.9 actualizada com a ingestão;
- `docs/knowledge/BASE-43-knowledge-file-ingestion.md` — relatório da
  base.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). `ingest.py` depende de
`knowledge.base` e `knowledge.metadata`; **nenhuma aresta nova** em
`FRONTEIRAS`. Âmbito lexical completo: contrato → registo → metadados →
índice → persistência → contexto → ingestão.

### Validação

```text
py -3.12 -m pytest   →   491 passed (482 anteriores + 9 ingestão)
```

### Próximo passo

**Decisão material terminal da Fase 9** — enriquecimento semântico
(embeddings via Model/Provider): exige planeamento próprio e decisões
documentadas (modelo/fornecedor, integração Provider/Runtime,
aditividade sobre o índice léxico) antes de qualquer motor de embeddings
(`PROJECT_STATE.md`, regra de continuação).

---

## 2026-09-09 — Knowledge Context Builder — Fase 9.6 (fecho do núcleo)

### Objectivo

Montar o pacote de contexto textual determinista a partir do índice (9.4)
e dos registos (9.5), fechando o circuito do núcleo reversível da Fase 9.
Sem I/O, sem modelos e sem decisão arquitectural material.

### Realizado

- `src/wsai2/knowledge/context.py` (novo): `ContextBuilder` (build com
  `top`/`snippet_caracteres`), `ContextEntry` e `KnowledgeContext` (com
  representação textual `text()` estável);
- `src/wsai2/knowledge/__init__.py` — exporta `ContextBuilder`,
  `ContextEntry`, `KnowledgeContext`;
- `tests/test_knowledge_context.py` (novo, **8 testes**);
- `ARCHITECTURE.md` — secção 3.9 actualizada com a construção de contexto;
- `docs/knowledge/BASE-42-knowledge-context-builder.md` — relatório da
  base.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). `context.py` depende apenas
de `knowledge.base` e `knowledge.index`; **nenhuma aresta nova** em
`FRONTEIRAS`. Com esta unidade, o núcleo reversível da Fase 9 está
completo (contrato → registo → metadados → índice → persistência →
contexto).

### Validação

```text
py -3.12 -m pytest   →   482 passed (474 anteriores + 8 contexto)
```

### Próximo passo

**Ingestão semântica real** (ficheiros do projecto + embeddings via
Model/Provider) — ponto de decisão seguinte: exige planeamento próprio e
decisões documentadas antes de motores de embeddings
(`PROJECT_STATE.md`, regra de continuação). A Fase 9 está funcionalmente
completa no núcleo reversível.

---

## 2026-09-09 — Knowledge SQLite Persistence — Fase 9.5

### Objectivo

Tornar o conhecimento persistente entre execuções, com a **decisão da
unidade consultada: persistência SQLite local** (estratégia de
armazenamento da recuperação). Embeddings continuam fora desta unidade.

### Realizado

- `src/wsai2/knowledge/storage.py` (novo): `KnowledgeStore` — esquema
  `knowledge_record` (id PK), `save`/`save_all` (upsert pelo id),
  `delete`/`count`/`load` (ordenada por id), metadados serializados em
  JSON (`ensure_ascii=False`), criação automática do directório pai;
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeStore`;
- `tests/test_knowledge_storage.py` (novo, **8 testes**);
- `ARCHITECTURE.md` — secção 3.9 actualizada com a persistência;
- `docs/knowledge/BASE-41-knowledge-sqlite-persistence.md` — relatório da
  base + registo da decisão de armazenamento.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). `storage.py` usa apenas
stdlib (`sqlite3`, `json`, `pathlib`, `contextlib`) — transversal
Windows/Linux; **nenhuma aresta nova** em `FRONTEIRAS`. I/O e estado
persistente introduzidos pela decisão documentada (ficheiro `.db`;
reversível ao nível da implementação).

### Validação

```text
py -3.12 -m pytest   →   474 passed (466 anteriores + 8 armazenamento)
```

### Próximo passo

Fase 9.6 — construção de contexto: montagem textual determinista a partir
do índice (9.4) e dos registos persistidos (9.5) — unidade pura e
directamente dependente, executável autonomamente. Ingestão semântica
real (ficheiros/embeddings) é ponto de paragem seguinte com planeamento
próprio.

---

## 2026-09-09 — Knowledge In-Memory Index — Fase 9.4

### Objectivo

Dotar o Knowledge Engine de consulta por termos sobre o conhecimento
admitido, com decisão da unidade consultada: **índice em memória puro**
(reversível, sem I/O, persistência ou embeddings). A estratégia de
armazenamento/embeddings fica adiada para a recuperação (9.5).

### Realizado

- `src/wsai2/knowledge/index.py` (novo): `KnowledgeIndex` — índice
  invertido com pesos de campo (título 3, etiquetas 2, conteúdo 1),
  `build`/`index`/`unindex`/`search`/`len`, reindexação por substituição
  e ordenação determinista (pontuação e `id`);
- `src/wsai2/knowledge/metadata.py` — novo `tokenize()` (normalização
  partilhada de termos); `derive_tags` passa a usá-la sem mudança de
  comportamento;
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeIndex` e `tokenize`;
- `tests/test_knowledge_index.py` (novo, **11 testes**);
- `ARCHITECTURE.md` — secção 3.9 actualizada com o índice;
- `docs/knowledge/BASE-40-knowledge-in-memory-index.md` — relatório da
  base + registo da decisão da unidade.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). Dependências internas ao
subsistema (base/registry/metadata); **nenhuma aresta nova** em
`FRONTEIRAS`. Decisão documentada: memória pura; persistência/embeddings
na 9.5 com decisão própria.

### Validação

```text
py -3.12 -m pytest   →   466 passed (455 anteriores + 11 índice)
```

### Próximo passo

Fase 9.5 — recuperação/construção de contexto: **interrompida até decisão
documentada** sobre armazenamento/embeddings (`PROJECT_STATE.md`, regra de
continuação). Paragem para decisão.

---

## 2026-09-09 — Knowledge Metadata Extraction — Fase 9.3

### Objectivo

Derivar `KnowledgeMetadata` estruturado (idioma, etiquetas, proveniência)
a partir do conteúdo/fonte de um `KnowledgeRecord`, de forma heurística e
determinista, sem I/O, sem modelos e sem decisão arquitectural material.

### Realizado

- `src/wsai2/knowledge/metadata.py` (novo): `KnowledgeMetadataExtractor`
  (completa idioma e etiquetas em falta; preserva `source`/`author`/
  `extras`), `detect_language` (marcadores por idioma, `"und"` no
  indeciso) e `derive_tags` (termos frequentes, excluindo palavras de
  ligação, respeitando limite);
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeMetadataExtractor`,
  `detect_language` e `derive_tags`;
- `tests/test_knowledge_metadata.py` (novo, **14 testes**);
- `ARCHITECTURE.md` — secção 3.9 actualizada com a extracção;
- `docs/knowledge/BASE-39-knowledge-metadata-extraction.md` — relatório
  da base.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). `metadata.py` depende apenas
de `knowledge.base`; **nenhuma aresta nova** em `FRONTEIRAS`. Não foi
abordada extracção semântica via Model/Provider nem indexação — ficam
para unidades posteriores com decisão própria.

### Validação

```text
py -3.12 -m pytest   →   455 passed (441 anteriores + 14 extracção)
```

### Próximo passo

Fase 9.4 — indexação: **exigirá decisão documentada** sobre estratégia de
armazenamento/embeddings antes de qualquer persistência
(`PROJECT_STATE.md`, regra de continuação). Paragem para decisão.

---

## 2026-09-09 — Knowledge Registry — Fase 9.2

### Objectivo

Dar ao Knowledge Engine o registo central de `KnowledgeRecord` (admissão
por id único, duplicações rejeitadas), seguindo o padrão dos registos das
Fases 4–8, sem I/O, indexação ou persistência.

### Realizado

- `src/wsai2/knowledge/registry.py` (novo): `KnowledgeRegistry` —
  catálogo com `register` (unicidade de id, `wsai.knowledge.duplicate`),
  `unregister`/`get`/`has`/`all`/`len` e `supported_contract_version`
  (ancorado a `KNOWLEDGE_CONTRACT_VERSION = "1.0"`);
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeRegistry`;
- `tests/test_knowledge_registry.py` (novo, **8 testes**) — admissão,
  duplicação, consultas, ordem, remoção e tipos distintos;
- `tests/test_architecture_contract.py` — nova aresta `FRONTEIRAS`:
  `("knowledge", "core")` (justificação documental em BASE-38);
- `ARCHITECTURE.md` — secção 3.9 actualizada com o registo;
- `docs/knowledge/BASE-38-knowledge-registry.md` — relatório da base.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). `knowledge` consume a
taxonomia `wsai2.core.errors` (`ValidationError`), padrão de todos os
registos das Fases 4–8; aresta nova autorizada `knowledge→core`, para
dentro, sem ciclos. Nenhum módulo das Fases 1–9.1 foi alterado.

### Validação

```text
py -3.12 -m pytest   →   441 passed (433 bases anteriores + 8 registo)
```

### Próximo passo

Fase 9.3 — extracção de metadados: derivar `KnowledgeMetadata` a partir
de conteúdo/fonte (idioma, etiquetas, proveniência), preparando a
indexação. Semântica via Model/Provider fica para unidade posterior com
decisão própria.

---

## 2026-09-09 — Knowledge Contract — Fase 9.1

### Objectivo

Iniciar a Fase 9 — Knowledge Engine com o contrato declarativo do
subsistema 3.9, autorizada após o fecho formal da Fase 8, seguindo o
padrão das fases anteriores (unidade declarativa primeira), sem I/O,
indexação ou recuperação.

### Realizado

- `src/wsai2/knowledge/base.py` (novo): `KNOWLEDGE_CONTRACT_VERSION`
  (`"1.0"`), `KnowledgeKind` (`document`/`extract`/`note`),
  `KnowledgeMetadata` (frozen: source, language, author, tags, extras) e
  `KnowledgeRecord` (frozen, validado em `__post_init__`);
- `src/wsai2/knowledge/__init__.py` — exports públicos do submódulo;
- `tests/test_knowledge.py` (novo, **10 testes**) — contrato, validação,
  imutabilidade, defaults, enums, versão e resumo;
- `tests/test_architecture_contract.py` — `knowledge` sai de
  `SUBSISTEMAS_FUTUROS` (fica `("api", "ui")`); justificação documental
  da decisão de fronteira;
- `ARCHITECTURE.md` — secção 3.9 expandida; secção 7 actualizada
  (Fase 8 fechada, Fase 9 em curso);
- `BASE-31` — regra 9 alinhada com a autorização de `knowledge`;
- `docs/knowledge/BASE-37-knowledge-engine-contract.md` — relatório da base.

### Arquitectura abrangida

Fase 9 — Knowledge Engine (subsistema 3.9). `knowledge` é **folha** nesta
unidade: depende apenas de stdlib, sem arestas novas em `FRONTEIRAS`.
Nenhum módulo das Fases 1–8 foi alterado. Decisão de fronteira registada:
a criação do subsistema foi autorizada pelo estado persistente/roadmap
(gate de fundação aprovado) e documentada em BASE-37.

### Validação

```text
py -3.12 -m pytest   →   433 passed (423 bases anteriores + 10 knowledge)
```

### Próximo passo

Fase 9.2 — Knowledge Registry: registo central de `KnowledgeRecord`
(admissão por id, duplicações rejeitadas), no padrão dos registos das
Fases 4–8, sem I/O.

---

## 2026-09-09 — Fecho formal da Fase 8 — validação da fundação

### Objectivo

Fechar formalmente a Fase 8 — Runtime Engine após o gate de validação da
fundação, registando a evidência necessária no estado persistente sem
alterar código funcional.

### Realizado

- resolvida a lacuna documental do log (entrada do residual 3 abaixo) e
  completado o relatório persistente truncado — W-01 do gate
  `/wsai-validate foundation`;
- reexecução da suíte completa: **423/423 testes aprovados**;
- criado `docs/validation/FOUNDATION_VALIDATION_REPORT.md` com a estrutura
  oficial (10 secções): execução, inventário, análise arquitectural,
  problemas e decisão do gate;
- decisão do gate: **🟡 APPROVED WITH WARNINGS** (apenas avisos P3
  documentados: FV-02 CI remota não confirmada, FV-04 ordem de prioridade
  duplicada; sem bloqueadores);
- `PROJECT_STATE.md` e `ROADMAP.md` actualizados para **FASE 8 CONCLUÍDA**.

### Arquitectura abrangida

Fecho de governação da Fase 8 (subsistema 3.8 e residuais Via B). Sem
alterações a `src/wsai2`; apenas documentação e estado persistente.

### Validação

```text
py -3.12 -m pytest          →   423 passed
/wsai-validate foundation   →   APPROVED WITH WARNINGS
```

### Próximo passo

Fase 9 — Knowledge Engine (ingestão). Gate de fundação satisfeito; a
Fase 9 requer auditoria/planeamento dedicado do subsistema 3.9 (novo) —
decisão arquitectural material a executar em unidade própria.

---

## 2026-09-08 — Filas multicamadas — Fase 8 residual 3 (Via B)

### Objectivo

Fechar o último residual funcional da Fase 8 (Via B): introduzir uma camada
de filas por prioridade com backlog, capacidade opcional e preempção de
trabalho ainda **pendente**, sem substituir nem alterar destrutivamente o
caminho directo do `Scheduler`.

### Realizado

- `src/wsai2/runtime_engine/queue.py` (novo): `MultilayerExecutionQueue`
  (genérica e thread-safe), `QueueItem`, `QueueSnapshot` e
  `priority_for_plan`;
- camada pronta ordenada por prioridade (`CRITICAL`/`HIGH`/`NORMAL`/`LOW`),
  backlog de espera, capacidade opcional `max_ready`, preempção apenas de
  itens ainda não iniciados (nenhum trabalho em curso é interrompido),
  promoção automática do backlog e operações `snapshot()`/`pending()`/`clear()`;
- integração **opt-in** no `Scheduler.run(queue=...)`; `queue=None` preserva
  exactamente a via directa histórica;
- exportação pública em `wsai2.runtime_engine` (`__init__.py`);
- `tests/test_runtime_engine_queue.py` (novo, **8 testes**) — fila e
  integração com o Scheduler;
- `.github/workflows/tests.yml` — execução da suíte no GitHub Actions
  (Python 3.12);
- alinhamento documental de `ARCHITECTURE.md`, `CORE_HARDENING_PLAN.md`,
  `ROADMAP.md` e `PROJECT_STATE.md` (resolução FV-01).

### Arquitectura abrangida

Fase 8 — Runtime Engine (`wsai2.runtime_engine`, subsistema 3.8). Camada
aditiva; sem arestas novas em `FRONTEIRAS`; stdlib `heapq`/`threading` e
reutilização de `wsai2.core.context` (`ExecutionPriority`) e
`wsai2.core.errors` (`ValidationError`). `ExecutionPlan` importado apenas em
`TYPE_CHECKING`.

### Resultado

`MultilayerExecutionQueue` funcional e testado; Scheduler com fila opcional
mantendo a via histórica. Unidade registada no `PROJECT_STATE`.

### Validação

```text
py -3.12 -m pytest   →   423 passed (415 bases anteriores + 8 filas)
```

### Próximo passo

Fecho formal da Fase 8: reexecução da suíte, `/wsai-validate foundation` e
relatório persistente.

---

## 2026-09-08 — Concorrência entre planos — Fase 8 residual (Via B)

### Objectivo

Fechar a unidade 2 dos residuais da Fase 8 (Via B): dar ao `Scheduler` a
capacidade de executar vários planos em paralelo de forma **aditiva e
opcional**, preservando o agendamento sequencial determinístico por
prioridade como comportamento por omissão, e a governação de recursos
partilhada em execução paralela.

### Realizado

- `Scheduler.run` ganha o kwarg aditivo `concurrency: int = 1` — com `1`
  usa o caminho sequencial histórico (extraído para `_agendar_sequencial`,
  comportamento intacto) e com `> 1` executa em paralelo
  (`_agendar_paralelo` via `ThreadPoolExecutor`);
- contextos materializados no thread principal com `execution_id` únicos
  (duplicações rejeitadas antes de executar — `wsai.runtime.duplicate_execution`);
- `stop_on_failure` paralelo: falha sinaliza um evento e os planos ainda
  não iniciados são descartados (os em curso concluem e são reportados);
- `step_runner` propagado do scheduler ao gestor (aditivo);
- `ResourceGovernor` passa a **thread-safe** (trinco sobre o livro de
  alocações e o contador) — dependência necessária para planos paralelos
  partilharem a mesma instância com contracepção de recursos;
- `tests/test_runtime_engine_concurrency.py` (novo, 10 testes) — validação,
  equivalência sequencial, sobreposição real (barrier), ordem de
  prioridade, `stop_on_failure` determinístico, falha parcial, monitor,
  governador partilhado e unicidade de `execution_id`.

### Arquitectura abrangida

Fase 8 — Runtime Engine (`wsai2.runtime_engine`, subsistema 3.8) +
`wsai2.resource` (thread-safety aditiva, sem mudança de semântica).
Sem arestas novas em `FRONTEIRAS`; stdlib `concurrent.futures`/`threading`.
Precedentes reutilizados: monitor thread-safe (residual 1), worker daemon
da 8.4, token cooperativo da 8.2. Filas multicamadas permanecem o residual 3.

### Resultado

`Scheduler` com execução paralela opcional; relatório em ordem de
prioridade nas duas vias; governador seguro em concorrência.
Unidade registada no `PROJECT_STATE` (baseline 415, Runtime Engine 99%).

### Validação

```text
py -3.12 -m pytest   →   415 passed (405 bases anteriores + 10 concorrência)
```

### Próximo passo

Unidade 3 dos residuais da Fase 8 — **Filas multicamadas** (última da
Fase 8): filas por prioridade com backlog sobre o scheduler actual,
aditivas, preservando o agendamento directo. A decisão pós-Gate (Via B)
está registada; a Fase 9 só é iniciada depois do fecho completo da Fase 8.

---

## 2026-09-08 — Monitorização contínua do Runtime — Fase 8 residual (Via B)

### Objectivo

Fechar a unidade 1 dos residuais da Fase 8 (Via B): observar execuções de
planos e agendamentos **em curso** — não apenas o relatório pós-facto da
8.5 — de forma aditiva, thread-safe e reversível, reutilizando
`FRONTEIRAS` e o determinismo do scheduler por omissão.

### Realizado

- `src/wsai2/runtime_engine/monitoring.py` (novo): `ExecutionMonitor` com
  hooks `on_execution_started` / `on_step_started` / `on_execution_finished`
  / `on_schedule_started` / `on_schedule_finished` e `snapshot()` protegido
  por `threading.Lock`; `ExecutionSnapshot` e `MonitorSnapshot` como API
  pública (execução em curso, passo actual, elapsed, marcos do scheduler);
- `RuntimeManager.execute_plan(..., monitor=None)` — ganchos de arranque,
  por passo e de finalização (inclui execuções negadas pela política, com
  passos `SKIPPED`);
- `Scheduler.run(..., monitor=None)` — propaga o monitor ao gestor e regista
  os marcos do agendamento;
- `runtime_engine/__init__.py` — exports públicos novos;
- `tests/test_runtime_engine_monitoring.py` (novo, 8 testes) — API, fotografia
  in-flight de outra thread, avanço de passos, falha, negação por política,
  reutilização do relatório final e propagação pelo scheduler;
- fakes em `tests/test_runtime_engine.py` actualizados para aceitar `monitor`.

### Arquitectura abrangida

Fase 8 — Runtime Engine (`wsai2.runtime_engine`, subsistema 3.8).
Alteração **100% aditiva e reversível**: sem o kwarg `monitor`, o
comportamento é idêntico ao das unidades anteriores; sem arestas novas em
`FRONTEIRAS`; `monitoring.py` depende só de `base.py` e da stdlib. A
medição de recursos do sistema (CPU/RAM/GPU) permanece no Runtime
Intelligence, fora desta unidade. Precedentes de concorrência reutilizados:
worker thread daemon da 8.4 e token de cancelamento da 8.2.

### Resultado

Observação contínua de execuções e agendamentos por interrogação em
qualquer momento; relatórios finais e scheduler determinístico intactos.
Unidade registada no `PROJECT_STATE` (baseline 405, Runtime Engine 97%).

### Validação

```text
py -3.12 -m pytest   →   405 passed (397 bases anteriores + 8 monitorização)
```

### Próximo passo

Unidade 2 dos residuais da Fase 8 — **Concorrência entre planos**:
execução paralela opcional no scheduler, aditiva, reutilizando o
`ExecutionMonitor`, preservando o scheduler determinístico por omissão.
A decisão pós-Gate (Via B) fica registada no `PROJECT_STATE`; a Fase 9 é
iniciada depois do fecho da Fase 8.

---

## 2026-09-08 — Gate — Core pronto para addons — Fase 8.9

### Objectivo

Formalizar o marco de addons do CORE_HARDENING_PLAN sem criar módulo
novo: instituir a política na fila (propagação no `Scheduler`), ligar o
contrato à segurança (ponte `permissions`→grants no `ExtensionRegistry`)
e dar ao Gate um critério executável (`tests/test_gate_addons.py`).

### Realizado

- `Scheduler.run` aceita `policy: PolicyEngine | None = None` e propaga-o
  ao `RuntimeManager` (autorização antes do passo 1, junto da fila);
- `ExtensionRegistry.register` aceita `policy` (opt-in) e concede as
  `permissions` declaradas como acções exactas ao principal = id da
  extensão (apenas após o registo ser aceite; sem policy, nada muda);
- `FRONTEIRAS` da 8.7 actualizadas com a aresta (`extension`,`security`);
- `tests/test_gate_addons.py` — fotografia executável do Gate (7 testes);
- 3 testes da ponte no `test_extension_registry.py`; mocks do scheduler
  actualizados no `test_runtime_engine.py`.

### Arquitectura abrangida

Fase 8 — Runtime Engine (marco do Gate). `wsai2.security` permanece
**folha**: a ponte vive no lado do registo (aresta nova `extension` ->
`security`, autorizada). Contrato de composição documentado: quem cria o
runtime passa o motor; quem executa trabalho de uma extensão leva
`principal` = `id` da extensão. Concorrência, filas multicamadas e
monitorização contínua permanecem unidades posteriores (não são
pré-requisitos do Gate).

### Resultado

A política passa a ser instituída na fila e ligada ao contrato; o Gate
tem critério executável (se os testes do Gate falharem, a base deixou de
satisfazer o marco). Alteração 100% aditiva — os 387 testes da base
permanecem aprovados.

### Validação

```text
py -3.12 -m pytest   →   397 passed (387 bases anteriores + 10 gate/ponte)
```

### Próximo passo

Decisão material pós-Gate: Fase 9 — Knowledge Engine (ingestão,
extracção, metadados) ou fechar primeiro a monitorização contínua e,
depois, concorrência/filas do Runtime. A registar no `PROJECT_STATE`.

---

## 2026-09-08 — Security/Policy + Project Isolation — Fase 8.8

### Objectivo

Cumprir os hardening 09 (Security/Policy) e 10 (Project Isolation) do
CORE_HARDENING_PLAN, pré-requisitos do Gate de addons: novo subsistema
folha `wsai2.security` com decisão exact-match por acção e fronteira de
projectos, mais o enforcement no Runtime Engine antes do passo 1.

### Criado

- `src/wsai2/security/base.py`
- `src/wsai2/security/policy.py`
- `src/wsai2/security/isolation.py`
- `src/wsai2/security/__init__.py`
- Actualizado `src/wsai2/core/context.py` (campo aditivo `principal`)
- Actualizado `src/wsai2/runtime_engine/manager.py` (`policy` opcional)
- Actualizado `tests/test_architecture_contract.py` (FRONTEIRAS +2)
- `tests/test_security_policy.py`, `tests/test_security_isolation.py`,
  `tests/test_security_integration.py`
- `docs/security/BASE-32-security-policy-isolation.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine (hardening 09 + 10). `wsai2.security` é folha:
depende só de `wsai2.core` (erros e contexto); `runtime_engine` passa a
depender de `security` (sem ciclo). Decisões registadas: uma unidade para
09+10; exact-match por acção (negação por omissão, sem RBAC); enforcement
antes do passo 1 no `execute_plan` (negação = report FAILED com
`PermissionError`, passos SKIPPED, runner nunca chamado); principal
aditivo no `ExecutionContext` (exigido apenas quando há política);
política injectada (sem motor, comportamento 8.5 preservado). A taxonomia
`PermissionError`/`ProjectIsolationError` da 8.2 ganha emissores reais.

### Resultado

`PolicyEngine.decide(principal, project_id, action)` devolve
`PolicyDecision` pura; `denied_decision` converte a negação no erro
taxonómico; `require_project`/`assert_same_project` impõem a fronteira de
projecto com `ProjectIsolationError`. O `RuntimeManager` aplica a política
antes do passo 1 quando fornecida. Alteração 100% aditiva — os 364 testes
da base permanecem aprovados.

### Validação

```text
py -3.12 -m pytest   →   387 passed (364 bases anteriores + 23 security/isolamento)
```

### Próximo passo

Gate — Core pronto para addons (formalização): validar a base completa,
confirmar os pré-requisitos com a cobertura existente e decidir onde a
política real é instituída (e como `permissions` do `ExtensionContract`
alimentam o `PolicyEngine`). Concorrência e monitorização permanecem
unidades posteriores; a Fase 9 — Knowledge Engine arranca depois do Gate.

---

## 2026-09-08 — Architecture Contract Tests — Fase 8.7

### Objectivo

Fechar o hardening 11 do CORE_HARDENING_PLAN e a "ordem recomendada" da
Fase 8: transformar as regras da CONSTITUTION/AGENTS em testes
executáveis sobre o repositório real, sem alterar código de produção.

### Criado

- `tests/test_architecture_contract.py`
- `docs/architecture/BASE-31-architecture-contract-tests.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine (hardening 11, último passo antes do Gate de
addons). Testes estáticos (ast/pathlib, stdlib), idênticos em Windows e
Linux. Regras cobertas: ARTIGO 1/10 (responsabilidade, documentação),
ARTIGO 2/13 (dependências para dentro, sem ciclos em runtime),
ARTIGO 4 (code de SO isolado, entrada só via `get_platform`), ARTIGO 8
(crescimento controlado, sem pastas placeholder nem subsistemas antecipados
api/ui/knowledge), ARTIGO 9 (testes sem recursos externos). A lista
`FRONTEIRAS` (21 arestas autorizadas entre subsistemas) foi fotografada
em auditoria e cresce apenas com justificação documental.

### Resultado

10 testes: docstring em todos os fontes; BASE-*.md por subsistema;
arestas respeitam `FRONTEIRAS`; imports apontam para subsistemas reais;
adaptadores de SO inacessíveis fora da plataforma; `get_platform` como
ponto único de entrada; Windows/Linux não se importam entre si; grafo de
runtime acíclico (imports `TYPE_CHECKING` excluídos); api/ui/knowledge
não antecipados; nenhuma pasta placeholder (__init__ re-exporta).
Alteração 100% aditiva — nenhum módulo de produção foi tocado.

### Validação

```text
py -3.12 -m pytest   →   364 passed (354 bases anteriores + 10 contrato arquitectural)
```

### Próximo passo

Decisão arquitectural material — Security / Policy (hardening 09) e
Project Isolation (hardening 10), pré-requisitos do Gate de addons:
modelar `principal → project → capability → resource → action → policy →
decision` e a propagação/preservação de `project_id` nas fronteiras. Sem
módulo próprio na Fase 8 e com contrato novo — exige auditoria e
planeamento dedicados antes de implementar.

---

## 2026-09-08 — Extension Lifecycle + Compatibility — Fase 8.6

### Objectivo

Fechar os hardening 02 (ciclo de vida de extensões, isolamento de falhas)
e 08 (compatibilidade/versioning de contratos) do CORE_HARDENING_PLAN:
implementar a máquina de lifecycle, o registo de extensões e a rejeição
de contratos incompatíveis **antes** do registo/execução. Unidade 100%
aditiva sobre a 8.1 — o `base.py` não foi alterado.

### Criado

- `src/wsai2/extension/versioning.py`
- `src/wsai2/extension/lifecycle.py`
- `src/wsai2/extension/registry.py`
- Actualizado `src/wsai2/extension/__init__.py` (novos exports)
- `tests/test_extension_versioning.py`
- `tests/test_extension_lifecycle.py`
- `tests/test_extension_registry.py`
- `docs/extension/BASE-30-extension-lifecycle-compatibility.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine. Subsistema 3.8 (extensões). Direcção de
dependências mantida para dentro (`wsai2.core.errors` + `.base` do próprio
subsistema). Decisões registadas: compatibilidade = **mesmo major**
(formato `major.minor`, sem patch); `SUPPORTED_CONTRACT_VERSION = "1.0"`;
rejeição antes do registo (`wsai.extension.contract_version`,
`wsai.extension.contract_incompatible`); `register` exige `VALIDATED`
e move para `REGISTERED`; `transition` é pura (devolve novo contrato
`frozen`, nunca executa acções) — uma transição inválida é
`ValidationError` `wsai.extension.lifecycle` sem mutar estado global.
**Correcção:** o "RuntimeStatus do registo (8.1)" referido em relatórios
anteriores **não existe**; o estado de uma extensão é o próprio campo
`lifecycle` do `ExtensionContract`, mantido no `ExtensionRegistry` sem
duplicação.

### Resultado

`ContractVersion.parse`/`is_compatible_with` validam e comparam versões;
`lifecycle.valid_transitions`/`can_transition`/`transition` implementam o
diagrama DISCOVERED→VALIDATED→REGISTERED→INITIALIZING→READY→RUNNING→
DEGRADED/FAILED→STOPPING→STOPPED; `ExtensionRegistry` oferece
`register`/`unregister`/`get`/`has`/`all`/`state`/`transition_state` no
padrão das Fases 4–6. Foram adicionados os códigos
`wsai.extension.duplicate` e `wsai.extension.unknown`. Alteração 100%
aditiva — os 314 testes da base permanecem aprovados.

### Validação

```text
py -3.12 -m pytest   →   354 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine + 40 lifecycle/compatibilidade)
```

### Próximo passo

Fase 8.7 — Testes de contrato arquitectural (hardening 11): testes que
verificam no repositório as fronteiras de dependências, a ausência de
ciclos de import, o isolamento de código Windows/Linux e a documentação
por módulo — sem decisão arquitectural nova. Concorrência entre planos,
filas multicamadas e monitorização contínua ficam para unidades
posteriores (fora do âmbito da 8.6).

---

## 2026-09-08 — Runtime Engine — Fase 8.5

### Objectivo

Fechar o hardening 07 do CORE_HARDENING_PLAN: o Runtime Engine consome o
`ExecutionPlan` (Fase 7) e executa-o com as políticas centralizadas (8.4)
e a governação de recursos (8.3), produzindo um Execution Result com
observabilidade; e agenda múltiplos planos por prioridade de forma
determinística. Unidade puramente aditiva sobre 8.1–8.4.

### Criado

- `src/wsai2/runtime_engine/base.py`
- `src/wsai2/runtime_engine/manager.py`
- `src/wsai2/runtime_engine/scheduler.py`
- `src/wsai2/runtime_engine/__init__.py`
- `tests/test_runtime_engine.py`
- `docs/runtime_engine/BASE-29-runtime-engine.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine. Subsistema 3.8 da arquitectura.
`wsai2.runtime_engine` consome `wsai2.task` (`ExecutionPlan`),
`wsai2.execution` (`execute_with_policies`, 8.4), `wsai2.resource`
(`ResourceGovernor`, 8.3, injectado) e `wsai2.core` (contexto, prioridade,
erros). Nomenclatura `runtime_engine` distingue-se de `wsai2.runtime`
(Runtime Intelligence, Fase 3 — medição). Decisões registadas: o plano é
a unidade de políticas e o passo a unidade de observação; recuperação por
plano inteiro (registo limpo por tentativa); `step_runner` injectado
(opaco, sem conhecimento de fornecedores); erros normalizados na
taxonomia 8.2 (`wsai.execution.not_executable`,
`wsai.execution.step_failed`, `wsai.execution.task_mismatch`); o gestor
devolve relatório mesmo em falha; scheduler sequencial determinístico com
ordenação estável por prioridade.

### Resultado

`RuntimeManager.execute_plan` valida o plano e a coerência do contexto,
constrói o contexto por omissão, executa o plano com
`execute_with_policies` e devolve `ExecutionReport` (estados
SUCCESS/FAILED/CANCELLED/TIMEOUT, `StepOutcome` por passo com `SKIPPED`
após a primeira falha, erro taxonómico, duração). `Scheduler.run` ordena
por prioridade (CRITICAL > HIGH > NORMAL > LOW, estável) e devolve
`SchedulerReport` (contagens, ordem efectiva, duração), com
`stop_on_failure` opcional. Alteração 100% aditiva — os 292 testes da base
permanecem aprovados.

### Validação

```text
py -3.12 -m pytest -v   →   314 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine)
```

### Próximo passo

Fase 8.6 — Lifecycle + Compatibility (hardening 02 e 08): evoluir
`wsai2.extension.lifecycle` existente, amarrar o estado de execução das
extensões ao `RuntimeStatus` do registo (8.1) e adicionar
versioning/compatibilidade de contratos antes da execução. Concorrência
entre planos, filas multicamadas e monitorização contínua ficam para
unidades posteriores (fora do âmbito da 8.5).

---

## 2026-09-08 — Execution Policies — Fase 8.4

### Objectivo

Centralizar no Runtime Engine as políticas de execução (hardening 06 do
CORE_HARDENING_PLAN): enforcement de timeout, cancelamento cooperativo
(checkpoints) e recuperação (retry), para que os addons não inventem
mecanismos incompatíveis. Unidade puramente aditiva sobre 8.1–8.3.

### Criado

- `src/wsai2/execution/base.py`
- `src/wsai2/execution/runner.py`
- `src/wsai2/execution/__init__.py`
- `tests/test_execution_policies.py`
- `docs/execution/BASE-28-execution-policies.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine. Subsistema 3.8 da arquitectura.
`wsai2.execution` é um subsistema folha que compõe o `ExecutionContext`/
`CancellationToken` (8.2), a taxonomia de erros (8.2) e o
`ResourceGovernor` (8.3, via `TYPE_CHECKING`). Decisões registadas:
políticas fora do núcleo (o token continua thread-agnostic); thread worker
daemon nunca morta à força; último erro preservado no retry; retry
opt-in (tipos declarados); deadline efectiva = a mais curta; relógios e
`sleep` injectáveis; orçamento libertado em `finally`.

### Resultado

`TimeoutPolicy`/`DeadlineGuard`/`run_with_timeout` (enforce), checkpoints
de cancelamento/deadline, `RecoveryPolicy`/`run_with_recovery` (backoff
opcional) e `execute_with_policies` (checkpoint → timeout → recuperação →
reserva/libertação de recursos). Código de timeout estável
`wsai.timeout.exceeded`. Alteração 100% aditiva — os 264 testes da base
permanecem aprovados.

### Validação

```text
py -3.12 -m pytest -v   →   292 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution)
```

### Próximo passo

Fase 8.5 — Runtime Manager + Scheduler (consumir o `ExecutionPlan` da
Fase 7, lançar execuções com `execute_with_policies`, gerir filas,
prioridades e o ciclo de vida) — decisão arquitectural material a planejar
dedicadamente.

---

## 2026-09-08 — Resource Governance — Fase 8.3

### Objectivo

Evoluir a gestão de memória existente para governação de recursos
(hardening 05 do CORE_HARDENING_PLAN): normalizar limites declarativos
(`ResourceLimit`), validar folga efectiva contra os perfis de hardware e
runtime e contabilizar alocações/reservas (accounting) — sem duplicar
mecanismos de medição das Fases 2/3.

### Criado

- `src/wsai2/resource/base.py`
- `src/wsai2/resource/governor.py`
- `src/wsai2/resource/__init__.py`
- `tests/test_resource_governor.py`
- `docs/resource/BASE-27-resource-governance.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine. Subsistema 3.8 da arquitectura.
`wsai2.resource` é um subsistema folha que consome os perfis existentes
(`HardwareProfile`, `RuntimeProfile`), a taxonomia `wsai2.core.errors`
(`ResourceError`) e o contrato `ResourceLimit` (8.1, por `TYPE_CHECKING`).
Distinção mantida: `capacity` estrutural vs `available_now` de runtime;
VRAM em uso e espaço livre de disco sem leitura runtime — governados pela
capacidade estrutural (limitação documentada). Dimensões desconhecidas →
`UNRECOGNIZED` explícito, nunca silêncio. Accounting por instância, sem
estado global; `release` idempotente.

### Resultado

`ResourceGovernor` com `evaluate` (consulta), `allocate`/`release`
(reserva e libertação), `outstanding` e `committed_for`. Códigos de erro
`wsai.resource.insufficient|duplicate|unknown`. Alteração 100% aditiva —
os 243 testes da base permanecem aprovados.

### Validação

```text
py -3.12 -m pytest -v   →   264 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource)
```

### Próximo passo

Fase 8.4 — Timeout + Cancellation + Recovery (políticas de limite
temporal, cancelamento efectivo e recuperação sobre o `ExecutionContext`
e o modelo de erros existentes).

---

## 2026-09-08 — Execution Context + Error Model — Fase 8.2

### Objectivo

Criar a fundação transversal de execução da Fase 8: a taxonomia unificada
de erros (hardening 03) e o `ExecutionContext` com cancelamento
cooperativo (hardening 04), num submódulo folha `wsai2.core`. Sem lógica
de execução, scheduler ou governação efectiva — apenas contratos.

### Criado

- `src/wsai2/core/errors.py`
- `src/wsai2/core/context.py`
- `src/wsai2/core/__init__.py`
- `tests/test_core_errors.py`
- `tests/test_execution_context.py`
- `docs/core/BASE-26-execution-context-error-model.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine. Subsistema 3.8 da arquitectura.
`wsai2.core` é uma camada folha do núcleo (constituição, artigo 2).
`WsaiError` + 10 categorias (Validation, Capability, Model, Provider,
Resource, Timeout, Cancellation, Permission, ProjectIsolation, Execution)
com `code` estável; `ExecutionContext` imutável com deadline
(`time.monotonic`), token de cancelamento cooperativo, budget e
prioridade. Decisão registada: o orçamento reutiliza `ResourceLimit`
(8.1) apenas por `TYPE_CHECKING`, mantendo o núcleo folha em runtime e
evitando ciclo futuro quando a extensão adoptar a taxaonomia.

### Resultado

Taxonomia transversal pronta para captura (`pytest.raises`) e contexto
de execução com validação à criação. `AdapterError` e `ProviderProbeError`
das Fases 1–7 permanecem intactos; o alinhamento do `AdapterError` sobre
`ProviderError` fica documentado como unidade posterior. Os 221 testes da
base permanecem aprovados — alteração 100% aditiva.

### Validação

```text
py -3.12 -m pytest -v   →   243 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core)
```

### Próximo passo

Fase 8.3 — Resource Governance (CPU, RAM, GPU/VRAM, armazenamento/I/O,
tempo), evoluindo a gestão de memória existente sem duplicar mecanismos.

---

## 2026-09-08 — Extension Contract — Fase 8.1

### Objectivo

Definir o contrato mínimo declarativo para extensões (addons) do
WorkStation AI 2, iniciando a Fase 8 — Runtime Engine conforme o
CORE_HARDENING_PLAN (hardening 01). Unidade puramente declarativa, sem
lógica de execução, registo ou scheduler.

### Criado

- `src/wsai2/extension/base.py`
- `src/wsai2/extension/__init__.py`
- `tests/test_extension.py`
- `docs/extension/BASE-25-extension-contract.md`

### Arquitectura abrangida

Fase 8 — Runtime Engine. Subsistema 3.8 da arquitectura.
`ExtensionContract` declara identidade, versões (do contrato e da
extensão), tipo funcional (`ExtensionKind`), capacidades, dependências,
recursos, permissões e lifecycle (`ExtensionLifecycleState`, sequência do
hardening 02). O módulo é folha: depende apenas de stdlib e não acopla à
Capability/Provider/Model Intelligence (constituição, artigos 2 e 8).

### Resultado

Contrato imutável (`frozen`) validado à criação; enums de tipo
(analyst/code/agent/github_tool/mcp/utility) e de lifecycle (10 estados);
`ResourceLimit` declarativo. Os 209 testes da base permanecem intactos —
a alteração é aditiva, sem tocar em módulos das Fases 1–7.

### Validação

```text
py -3.12 -m pytest -v   →   221 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension)
```

### Próximo passo

Fase 8.2 — Execution Context + Error Model (transporte de execution_id,
task_id, deadline, cancellation, resource budget, prioridade; taxonomia
de erros transversal).

---

## 2026-09-08 — Task Intelligence (plano de execução) — Fase 7

### Objectivo

Integrar os requisitos, a viabilidade, a recomendação de modelo e um
fornecedor saudável num plano de execução determinístico, encerrando a
Fase 7.

### Criado

- `src/wsai2/task/plan.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_plan.py`
- `docs/task/BASE-24-task-intelligence-execution-plan.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
`build_execution_plan` fecha o ciclo (requisitos → capacidades →
modelo → fornecedor saudável → passos). A selecção de modelo e de
fornecedor permanece separada (constituição, artigo 13); o health check
dos fornecedores é injectado (`ProviderHealth`), sem I/O no plano.

### Resultado

`ExecutionPlan` (feasible, model_id, provider_id, reasons, steps) com
`is_executable`; escolha do fornecedor determinística (saudável + com
capacidades do modelo) e justificações de inviabilidade.

### Validação

```text
py -3.12 -m pytest -v   →   209 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task)
```

### Próximo passo

Iniciar a Fase 8 — Runtime Engine (subsistema 3.8).

---

## 2026-09-08 — Task Intelligence (selecção de capacidades) — Fase 7

### Objectivo

Verificar, contra o Capability Engine, quais das capacidades exigidas
por uma tarefa estão disponíveis, determinando a viabilidade da
execução.

### Criado

- `src/wsai2/task/capability_selection.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_capability_selection.py`
- `docs/task/BASE-23-task-intelligence-capability-selection.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
A selecção delega a avaliação ao Capability Engine (Fase 4); o Task
Intelligence separa capacidades satisfeitas e em falta e decide a
viabilidade, sem duplicar lógica.

### Resultado

`select_capabilities` devolve `TaskCapabilitySelection` (required /
available / missing / is_viable), preservando a ordem de declaração.

### Validação

```text
py -3.12 -m pytest -v   →   201 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 31 task)
```

### Próximo passo

Concluir a Fase 7 (plano de execução).

---

## 2026-09-08 — Task Intelligence (requisitos de tarefa) — Fase 7

### Objectivo

Materializar as exigências de uma tarefa (categoria, capacidades,
tokens) num contrato consumível pelo Model Intelligence.

### Criado

- `src/wsai2/task/requirements.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_requirements.py`
- `docs/task/BASE-22-task-intelligence-requirements.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
`TaskRequirements` agrega a categoria (da classificação) e as
capacidades exigidas pela tarefa — únicas, por ordem, sem invenção
(limite BASE-19).

### Resultado

`requirements_for` / `requirements_for_many` devolvem o contrato de
requisitos das tarefas; `capabilities_for_task` normaliza a lista.

### Validação

```text
py -3.12 -m pytest -v   →   194 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 24 task)
```

### Próximo passo

Continuar a Fase 7 (selecção de capacidades contra o Capability Engine).

---

## 2026-09-08 — Task Intelligence (classificação de tarefas) — Fase 7

### Objectivo

Classificar cada tarefa quanto à categoria de modelo mais adequada,
ligando o Task Intelligence ao Model Intelligence de forma
determinística.

### Criado

- `src/wsai2/task/classification.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_classification.py`
- `docs/task/BASE-21-task-intelligence-classification.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
`TaskClassification` mapeia o tipo funcional (TaskKind) para a
categoria de modelo (ModelCategory); a selecção de modelo e de
fornecedor permanece separada (constituição, artigo 13).

### Resultado

`classify_task` / `classify_tasks` devolvem a categoria adequada por
tarefa, com mapa determinístico documentado e ordem preservada.

### Validação

```text
py -3.12 -m pytest -v   →   186 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 16 task)
```

### Próximo passo

Continuar a Fase 7 (requisitos de tarefa).

---

## 2026-09-08 — Task Intelligence (contrato de tarefa) — Fase 7

### Objectivo

Iniciar a Fase 7 — Task Intelligence com o contrato de tarefa e a sua
representação, como definido na auditoria BASE-19.

### Criado

- `src/wsai2/task/base.py`
- `src/wsai2/task/__init__.py`
- `tests/test_task.py`
- `docs/task/BASE-20-task-intelligence-contract.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
A tarefa declara o que fazer (tipo funcional, texto, capacidades) sem
depender de modelos ou fornecedores (constituição, artigo 13).

### Resultado

`TaskKind` (chat / completion / embedding) e `Task` imutável com
`required_capabilities` e `metadata` opaca; valida prompt e max_tokens.

### Validação

```text
py -3.12 -m pytest -v   →   179 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 9 task)
```

### Próximo passo

Continuar a Fase 7 (classificação de tarefas).

---

## 2026-09-07 — Provider Layer (health checks) — Fase 6

### Objectivo

Concluir o Provider Layer com a saúde fina dos fornecedores
(saudável / degradado / indisponível), combinando detecção e
adaptadores, encerrando a Fase 6.

### Criado

- `src/wsai2/provider/health.py`
- Actualizado `src/wsai2/provider/__init__.py`
- `tests/test_provider_health.py`
- `docs/provider/BASE-18-provider-layer-health.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
Os health checks consomem a detecção e os adaptadores; a decisão é
pura e o I/O (probe + transporte) injectado. Fornecedores sem
adaptador são reportados como DEGRADED (não propagam erros).

### Resultado

`check_provider_health` / `check_providers_health` devolvem `ProviderHealth`
com contagem de modelos, latência e erro; `healthy_providers` filtra os
operacionais. Integração real validada contra servidor local.

### Validação

```text
py -3.12 -m pytest -v   →   170 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider)
```

### Próximo passo

Iniciar a Fase 7 — Task Intelligence (subsistema 3.7).

---

## 2026-09-07 — Provider Layer (adaptadores de runtime) — Fase 6

### Objectivo

Definir a interface estável de comunicação com os motores concretos
(listar modelos, gerar texto) por tipo de fornecedor, mantendo o I/O de
rede injectável e isolado do domínio.

### Criado

- `src/wsai2/provider/adapters.py`
- `src/wsai2/provider/transports.py`
- Actualizado `src/wsai2/provider/__init__.py`
- `tests/test_provider_adapters.py`
- `docs/provider/BASE-17-provider-layer-adapters.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
`RuntimeAdapter` (Protocol) com `OllamaAdapter` (protocolo nativo) e
`OpenAiCompatibleAdapter` (llama.cpp e APIs compatíveis); `build_adapter`
constrói por id de fornecedor; `http_json_transport` separa o I/O.

### Resultado

Toda a lógica dos adaptadores é testável sem rede (transport
injectável); erros normalizados em `AdapterError`; fábrica de
adaptadores por id cobrindo todo o catálogo base.

### Validação

```text
py -3.12 -m pytest -v   →   160 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 36 provider)
```

### Próximo passo

Concluir a Fase 6 (health checks: saúde fina por fornecedor).

---

## 2026-09-07 — Provider Layer (detecção) — Fase 6

### Objectivo

Detectar no ambiente real quais fornecedores do registo estão presentes
e acessíveis, separando a lógica de domínio do I/O de rede.

### Criado

- `src/wsai2/provider/detection.py`
- `src/wsai2/provider/probes.py`
- Actualizado `src/wsai2/provider/__init__.py`
- `tests/test_provider_detection.py`
- `docs/provider/BASE-16-provider-layer-detection.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
A detecção mantém o domínio puro (`detection.py`) e isola o contacto de
rede em probes injectáveis (`probes.py`), respeitando o artigo 5 da
constituição (código de I/O separado da lógica de domínio).

### Resultado

`detect_provider` / `detect_providers` devolvem `ProviderDetection`
(estado, latência, erro, capacidades) usando um `ProviderProbe`
injectável; `available_providers` filtra os acessíveis. `health_probe`
é o probe HTTP concreto isolado. Toda a lógica é testável sem rede.

### Validação

```text
py -3.12 -m pytest -v   →   146 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 22 provider)
```

### Próximo passo

Continuar a Fase 6 (adaptadores de runtime: interface estável de
comunicação por tipo de fornecedor).

---

## 2026-09-07 — Provider Layer (contratos e registo) — Fase 6

### Objectivo

Iniciar a Fase 6 — Provider Layer com os contratos de fornecedor e o
registo central, base declarativa para a detecção, os adaptadores e os
health checks das unidades seguintes.

### Criado

- `src/wsai2/provider/base.py`
- `src/wsai2/provider/registry.py`
- `src/wsai2/provider/__init__.py`
- `tests/test_provider.py`
- `docs/provider/BASE-15-provider-layer-contracts.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
Isola os fornecedores e motores concretos (runtimes locais e APIs
compatíveis) através de contratos estáveis.

### Resultado

`ProviderDefinition` com `ProviderType` (local_runtime / remote_api),
endpoint base predefinido e `capabilities_provided` (ligação ao
Capability Engine). `ProviderRegistry` com catálogo base (Ollama,
llama.cpp, API compatível com OpenAI). Domínio puro, sem dependências de
plataforma.

### Validação

```text
py -3.12 -m pytest -v   →   135 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 11 provider)
```

### Próximo passo

Continuar a Fase 6 (detecção de fornecedores presentes e acessíveis no
ambiente real).

---

## 2026-09-07 — Model Intelligence (recomendação) — Fase 5

### Objectivo

Concluir a Fase 5 — Model Intelligence com a recomendação do modelo
mais adequado (por categoria e score), com justificação e alternativas.

### Criado

- `src/wsai2/model/recommendation.py`
- Actualizado `src/wsai2/model/__init__.py` (exporta novos tipos e função)
- `tests/test_model_recommendation.py`
- `docs/model/BASE-14-model-intelligence-recommendation.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Fecho do item "recomendação" do roadmap da fase. Política determinística
documentada: candidatos com score > 0; ordenação por score, parâmetros,
RAM e id.

### Resultado

`recommend_model` devolve `ModelRecommendation` (modelo, categoria,
score, estado, razão e alternativas) ou `None` sem candidatos. Modelos
indisponíveis nunca são recomendados.

### Validação

```text
py -3.12 -m pytest -v   →   124 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model)
```

### Próximo passo

Iniciar a Fase 6 — Provider Layer (subsistema 3.6): contratos de
fornecedor, detecção, adaptadores de runtime e health checks.

---

## 2026-09-07 — Model Intelligence (classificação) — Fase 5

### Objectivo

Implementar a classificação dos modelos: categoria funcional primária e
score de adequação determinístico derivado da compatibilidade, base
para a recomendação.

### Criado

- `src/wsai2/model/classification.py`
- Actualizado `src/wsai2/model/base.py` (ModelCategory; campo category em ModelDefinition)
- Actualizado `src/wsai2/model/registry.py` (catálogo com categorias)
- Actualizado `src/wsai2/model/__init__.py` (exporta novos tipos e funções)
- `tests/test_model_classification.py`
- `docs/model/BASE-13-model-intelligence-classification.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Rubrica de classificação determinística (disponível=1.0, condicionado=0.5,
indisponível=0.0) aplicada sobre os veredictos de compatibilidade.

### Resultado

`classify_model`/`classify_models` devolvem `ModelClassification`
(categoria + score + veredicto). Categoria declarada na definição ou
derivada do tipo (LLM → chat; embedding → embedding).

### Validação

```text
py -3.12 -m pytest -v   →   114 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 32 model)
```

### Próximo passo

Continuar a Fase 5 (recomendação de modelos — encerra a fase).

---

## 2026-09-07 — Model Intelligence (compatibilidade) — Fase 5

### Objectivo

Implementar a compatibilidade dos modelos contra o hardware
estrutural, o estado do runtime e as capacidades requeridas do
Capability Engine, preparando a classificação e a recomendação.

### Criado

- `src/wsai2/model/compatibility.py`
- Actualizado `src/wsai2/model/base.py` (ModelState, ModelCheck, ModelVerdict)
- Actualizado `src/wsai2/model/__init__.py` (exporta novos tipos e funções)
- `tests/test_model_compatibility.py`
- `docs/model/BASE-12-model-intelligence-compatibility.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Compatibilidade com tripla dimensão: capacidades requeridas (Capability
Engine), requisitos estruturais (*Hardware Capability*) e requisitos de
runtime (*Runtime State*) — Artigo 5 da Constituição.

### Resultado

`evaluate_model`, `evaluate_models` e `compatible_models` devolvem
`ModelVerdict` com `ModelState`, verificações por requisito e
capacidades em falta. Capacidade em falta ou requisito estrutural
falhado → UNAVAILABLE; capacidade condicionada ou runtime insuficiente
→ RESTRICTED; caso contrário → AVAILABLE.

### Validação

```text
py -3.12 -m pytest -v   →   105 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 23 model)
```

### Próximo passo

Continuar a Fase 5 (classificação dos modelos e score de adequação para
recomendação).

---

## 2026-09-07 — Model Intelligence (registo e metadados) — Fase 5

### Objectivo

Iniciar a Fase 5 — Model Intelligence com o registo de modelos,
metadados e requisitos, base declarativa para a compatibilidade e a
recomendação das unidades seguintes.

### Criado

- `src/wsai2/model/base.py`
- `src/wsai2/model/registry.py`
- `src/wsai2/model/__init__.py`
- `tests/test_model.py`
- `docs/model/BASE-11-model-intelligence-metadata.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Mantém informação sobre modelos: metadados, requisitos e, nas unidades
seguintes, compatibilidade, desempenho e adequação às tarefas.

### Resultado

`ModelDefinition` com `ModelKind` (llm/embedding), `ModelMetadata`
(versão, parâmetros, janela de contexto, licença, arquitectura) e
`ModelRequirements` quantificados, com referência às capacidades do
sistema requeridas. `ModelRegistry` com catálogo base (Qwen 2.5 7B,
Phi-3 Mini, All MiniLM L6 v2). Domínio puro, sem dependências de
plataforma.

### Validação

```text
py -3.12 -m pytest -v   →   93 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 11 model)
```

### Próximo passo

Continuar a Fase 5 (compatibilidade dos modelos contra o sistema e as
capacidades requeridas).

---

## 2026-09-07 — Capability Engine (compatibilidade) — Fase 4

### Objectivo

Concluir a Fase 4 — Capability Engine com o relatório de
compatibilidade: consolidar a avaliação por capacidade com justificação
textual e fechar o catálogo de capacidades disponíveis.

### Criado

- `src/wsai2/capability/compatibility.py`
- Actualizado `src/wsai2/capability/base.py` (CapabilityCompatibility, CompatibilityReport)
- Actualizado `src/wsai2/capability/__init__.py` (exporta novos tipos e build_compatibility)
- `tests/test_capability_compatibility.py`
- `docs/capability/BASE-10-capability-engine-compatibility.md`

### Arquitectura abrangida

Fase 4 — Capability Engine. Subsistema 3.4 da arquitectura.
Relatório consolidado que fecha todos os itens do roadmap da fase
(definições, registo, avaliação, compatibilidade, capacidades
disponíveis).

### Resultado

`build_compatibility` devolve um `CompatibilityReport` com uma
`CapabilityCompatibility` por capacidade registada: estado,
`justification` em linguagem natural (exigido vs disponível) e
agrupamentos available/restricted/unavailable — o catálogo final.

### Validação

```text
py -3.12 -m pytest -v   →   82 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability)
```

### Próximo passo

Iniciar a Fase 5 — Model Intelligence (subsistema 3.5): registo de
modelos, metadados, requisitos, classificação e recomendação.

---

## 2026-09-07 — Capability Engine (avaliação) — Fase 4

### Objectivo

Implementar a avaliação das capacidades contra o hardware estrutural
(`HardwareProfile`) e o estado do runtime (`RuntimeProfile`), distinguindo
*Hardware Capability* de *Runtime State* e preparando a compatibilidade
e o catálogo de capacidades disponíveis.

### Criado

- `src/wsai2/capability/evaluation.py`
- Actualizado `src/wsai2/capability/base.py` (CapabilityState, RequirementCheck, CapabilityVerdict)
- Actualizado `src/wsai2/capability/__init__.py` (exporta novos tipos e funções)
- `tests/test_capability_evaluation.py`
- Correggido `tests/test_runtime.py` (cpu_percent de processos pode exceder 100% em Windows)
- `docs/capability/BASE-09-capability-engine-evaluation.md`

### Arquitectura abrangida

Fase 4 — Capability Engine. Subsistema 3.4 da arquitectura.
Avaliação com veredictos disponível/condicionada/indisponível e
verificações por requisito, respeitando a separação entre capacidade de
hardware e estado do runtime (Artigo 5 da Constituição).

### Resultado

`evaluate_capability`, `evaluate_capabilities` e `available_capabilities`
devolvem `CapabilityVerdict` com `CapabilityState` e `RequirementCheck`
por requisito (ram_total, ram_available, cpu_cores, gpu, disk). Falha
estrutural → UNAVAILABLE; falha de runtime → RESTRICTED; caso contrário
→ AVAILABLE.

### Validação

```text
py -3.12 -m pytest -v   →   70 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 21 capability)
```

### Próximo passo

Continuar a Fase 4 (compatibilidade: relatório consolidado por
capacidade, fechando o catálogo de capacidades disponíveis).

---

## 2026-09-07 — Capability Engine (definições e registo) — Fase 4

### Objectivo

Iniciar a Fase 4 — Capability Engine com as definições de capacidade e
o registo central, base declarativa para a avaliação e para as
capacidades disponíveis.

### Criado

- `src/wsai2/capability/base.py`
- `src/wsai2/capability/registry.py`
- `src/wsai2/capability/__init__.py`
- `tests/test_capability.py`
- `docs/capability/BASE-08-capability-engine-definitions.md`

### Arquitectura abrangida

Fase 4 — Capability Engine. Subsistema 3.4 da arquitectura.
Determina as capacidades reais que o sistema consegue disponibilizar.

### Resultado

`CapabilityDefinition` com `CapabilityRequirements` quantificados e
`CapabilityRegistry` com catálogo base (inferência local, embeddings,
ML acelerado, processamento leve). Domínio puro, sem dependências de
plataforma.

### Validação

```text
py -3.12 -m pytest -v   →   60 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 11 capability)
```

### Próximo passo

Continuar a Fase 4 (avaliação das capacidades contra hardware e runtime,
compatibilidade, capacidades disponíveis).

---

## 2026-09-07 — Runtime Intelligence (disponibilidade efectiva) — Fase 3

### Objectivo

Concluir a Fase 3 — Runtime Intelligence com a análise derivada de
disponibilidade efectiva: até que ponto os recursos estão livres para
trabalho no momento da amostragem.

### Criado

- `src/wsai2/runtime/availability.py`
- Actualizado `src/wsai2/runtime/base.py` (AvailabilityDomain, AvailabilityStatus, RuntimeAvailability, RuntimeProfile expandido)
- Actualizado `src/wsai2/runtime/factory.py` (integra analyze_runtime_availability)
- Actualizado `src/wsai2/runtime/__init__.py` (exporta novos tipos)
- `tests/test_runtime.py` (expandido com 10 testes)
- `docs/runtime/BASE-07-runtime-availability.md`

### Arquitectura abrangida

Fase 3 — Runtime Intelligence. Subsistema 3.3 da arquitectura.
Conclui *Runtime State* com avaliação derivada de disponibilidade,
distinta de *Hardware Capability* (Artigo 5 da Constituição).

### Resultado

`RuntimeProfile` completo com 2 disponibilidades (cpu, memory), scores
0.0–1.0, estados HEALTHY–CRITICAL, `overall_status` ponderado,
acessores de conveniência e resumo textual de disponibilidade.

### Validação

```text
py -3.12 -m pytest -v   →   49 passed (3 fundação + 5 platform + 17 hardware + 24 runtime)
```

### Próximo passo

Iniciar Fase 4 — Capability Engine (definições de capacidade, registo,
avaliação, compatibilidade, capacidades disponíveis).

---

## 2026-09-07 — Runtime Intelligence (estado de execução) — Fase 3

### Objectivo

Iniciar a Fase 3 — Runtime Intelligence com o estado de execução do
sistema: carga de CPU, utilização de memória, processos activos e
tempo de actividade, mantendo-o separado da capacidade estrutural.

### Criado

- `src/wsai2/runtime/base.py`
- `src/wsai2/runtime/cpu.py`
- `src/wsai2/runtime/memory.py`
- `src/wsai2/runtime/processes.py`
- `src/wsai2/runtime/factory.py`
- `src/wsai2/runtime/__init__.py`
- `tests/test_runtime.py`
- `docs/runtime/BASE-06-runtime-intelligence.md`

### Arquitectura abrangida

Fase 3 — Runtime Intelligence. Subsistema 3.3 da arquitectura.
Representa *Runtime State* — distinto de *Hardware Capability*
(Artigo 5 da Constituição).

### Resultado

`discover_runtime()` devolve um `RuntimeProfile` com `CpuLoad`,
`MemoryRuntime`, top de processos por memória RSS e `SystemUptime`,
tudo via psutil cross-platform com resumos textuais de apresentação.

### Validação

```text
py -3.12 -m pytest -v   →   39 passed (3 fundação + 5 platform + 17 hardware + 14 runtime)
```

### Próximo passo

Continuar a Fase 3 (análise de disponibilidade efectiva / health checks)
ou fechar a base e avançar para a Fase 4 — Capability Engine.

---

## 2026-09-07 — Hardware Intelligence (perfil e capacidades) — Fase 2

### Objectivo

Concluir a Fase 2 — Hardware Intelligence com perfil de hardware agregado
e capacidades estruturais derivadas (scoring, níveis, nível global).

### Criado

- `src/wsai2/hardware/profile.py`
- Actualizado `src/wsai2/hardware/base.py` (CapabilityLevel, CapabilityDomain, HardwareCapability, HardwareProfile expandido)
- Actualizado `src/wsai2/hardware/factory.py` (integra analyze_hardware_profile)
- Actualizado `src/wsai2/hardware/__init__.py` (exporta novos tipos)
- `tests/test_hardware.py` (expandido com 9 testes)
- `docs/hardware/BASE-05-hardware-profile-capabilities.md`

### Arquitectura abrangida

Fase 2 — Hardware Intelligence. Subsistema 3.2 da arquitectura.
Conclui *Hardware Capability* com análise derivada quantificada.

### Resultado

`HardwareProfile` completo com 4 capacidades (compute, memory, graphics, storage),
scores 0.0–1.0, níveis MINIMAL–HIGH_END, `overall_level` ponderado,
acessores de conveniência, resumos textuais para todos os domínios.

### Validação

```text
py -3.12 -m pytest -v   →   25 passed (3 fundação + 5 platform + 17 hardware)
```

### Próximo passo

Iniciar Fase 3 — Runtime Intelligence (recursos disponíveis, carga, processos, estado de execução).

---

## 2026-09-07 — Hardware Intelligence (GPU e armazenamento) — Fase 2

### Objectivo

Implementar a camada de abstração de plataforma (Platform Foundation) com
detecção de sistema operativo, adaptadores Windows/Linux e fábrica de
seleção, conforme Fase 1 do roadmap.

### Criado

- `src/wsai2/platform/__init__.py`
- `src/wsai2/platform/base.py`
- `src/wsai2/platform/windows.py`
- `src/wsai2/platform/linux.py`
- `src/wsai2/platform/factory.py`
- `tests/test_platform.py`
- `docs/platform/BASE-02-platform-foundation.md`

### Arquitectura abrangida

Fase 1 — Platform Foundation. Subsistema 3.1 da arquitectura. Isola
código específico de SO e expõe interface uniforme via `get_platform()`.

### Resultado

Plataforma detectada correctamente no Windows actual; adaptador Linux
presente e testável; fábrica selecciona adaptador adequado ao SO
corrente.

### Validação

```text
py -3.12 -m pytest -v   →   8 passed (3 fundação + 5 platform)
```

### Próximo passo

Iniciar Fase 2 — Hardware Intelligence (descoberta de CPU, memória,
GPU, armazenamento).

---

## 2026-09-07 — Fundação Python e base de testes

### Objectivo

Estabelecer a infraestrutura Python mínima do projecto e a configuração
inicial da base de testes, tornando verificável cada unidade futura.

### Criado

- `pyproject.toml`
- `src/wsai2/__init__.py`
- `src/wsai2/version.py`
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_foundation.py`
- `docs/foundation/BASE-01-fundacao-python-testes.md`
- `.gitignore`

### Arquitectura abrangida

Fase 0 — Fundação e Governação. Cria o pacote raiz `wsai2` e a base de
testes. Não implementa nenhum subsistema funcional.

### Resultado

Projecto Python instalável em modo editável e base de testes a funcionar.

### Validação

```text
py -3.12 -m pytest -v   →   3 passed
```

### Próximo passo

Concluir os restantes itens da Fase 0 (política de modelos OpenCode e
workflow de sincronização Git) ou iniciar a Fase 1 — Platform Foundation.

---

## 2026-09-07 — Inicialização do projecto

### Objectivo

Estabelecer a primeira base documental e de governação para o desenvolvimento do WorkStation AI 2.

### Criado

- `README.md`
- `AGENTS.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/CONSTITUTION.md`
- `docs/project/ROADMAP.md`
- `docs/project/PROJECT_STATE.md`
- `docs/project/IMPLEMENTATION_LOG.md`

### Arquitectura abrangida

Esta unidade estabelece as regras que irão governar todos os subsistemas futuros. Ainda não implementa Hardware Intelligence, Runtime Intelligence ou qualquer motor funcional.

### Resultado

A fundação documental inicial está estabelecida.

### Próximo passo

Implementar a camada de governação OpenCode:

1. skill central;
2. comando `/wsai-run`;
3. política de modelos;
4. workflow de sincronização Git.

### Validação

Os ficheiros foram criados no repositório remoto oficial.
