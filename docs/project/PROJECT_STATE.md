# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1 a 8.9 concluídas — Gate de addons aprovado; residuais Via B: monitorização ✓, concorrência ✓; filas multicamadas pendentes)

## Base actual

Unidade residual 2 da Fase 8 (Via B) — **Concorrência entre planos CONCLUÍDA**: `Scheduler.run` ganha o kwarg aditivo `concurrency` (por omissão `1` = agendamento sequencial histórico intacto; com `> 1`, execução paralela num `ThreadPoolExecutor` com relatório em ordem de prioridade). Contextos materializados no thread principal com `execution_id` únicos (duplicações rejeitadas); `stop_on_failure` descarta planos ainda não iniciados; `step_runner` propagado. `ResourceGovernor` passa a thread-safe (trinco sobre alocações) — dependência necessária para partilha segura entre planos paralelos. Baseline sobe para 415 (405 + 10 em `tests/test_runtime_engine_concurrency.py`). `FRONTEIRAS` intactas; filas multicamadas permanecem o residual 3.

## Última unidade concluída

Fase 8 — residual 2: **Concorrência entre planos** (relatório `docs/runtime_engine/BASE-35-runtime-engine-concurrency.md`). Aditiva e opcional; execução paralela sem alterar a semântica de cada plano; governação de recursos partilhada tornada thread-safe. Baseline de testes: 415.

## Próxima unidade

Implementar a **unidade 3 dos residuais da Fase 8 — Filas multicamadas**: filas por prioridade com backlog/preempção sobre o scheduler actual, aditivas, preservando o agendamento directo por omissão. A **decisão material pós-Gate** está registada (Via B: fechar primeiro os residuais do Runtime — monitorização ✓, concorrência ✓, filas multicamadas); a **Fase 9 — Knowledge Engine** só é iniciada depois do fecho completo da Fase 8.

## Subsistemas funcionais implementados:

- Platform Foundation (detecção e abstracção de SO)
- Hardware Intelligence (CPU, memória, GPU, armazenamento, perfil, capacidades)
- Runtime Intelligence (carga, memória, processos, uptime, disponibilidade)
- Capability Engine (definições, registo, avaliação, compatibilidade, capacidades disponíveis)
- Model Intelligence (registo, metadados, requisitos, compatibilidade, classificação, recomendação)
- Provider Layer (contratos, registo, detecção, adaptadores de runtime, health checks)
- Task Intelligence (contrato, classificação, requisitos, selecção de capacidades, plano de execução)
- Extension Contract (contrato mínimo declarativo de extensões — Fase 8.1)
- Execution Context + Error Model (camada transversal `wsai2.core` — Fase 8.2)
- Resource Governance (governador de orçamento e accounting `wsai2.resource` — Fase 8.3)
- Runtime Engine (gestor de execução e scheduler `wsai2.runtime_engine` — Fase 8.5)
- Monitorização contínua do Runtime (observação em curso de execuções e agendamentos `wsai2.runtime_engine.monitoring` — Fase 8 residual 1)
- Concorrência entre planos (execução paralela opcional no `Scheduler` `concurrency` + governador thread-safe — Fase 8 residual 2)
- Extension Lifecycle + Compatibility (máquina de lifecycle, registo e versioning de contratos `wsai2.extension` — Fase 8.6)
- Architecture Contract Tests (regras da Constituição executáveis — Fase 8.7)
- Security / Policy + Project Isolation (política exact-match e fronteira de projectos `wsai2.security` — Fase 8.8)
- Gate — Core pronto para addons (formalização do marco: critério executável + propagação da política no `Scheduler` + ponte `permissions`→grants no registo — Fase 8.9)

## Desenvolvimento controlado

A base de desenvolvimento está formalizada em `docs/project/CONTROLLED_DEVELOPMENT.md` e `docs/architecture/CORE_HARDENING_PLAN.md`.

A família oficial de comandos OpenCode do projecto é:

- `/wsai`
- `/wsai-run`
- `/wsai-audit`
- `/wsai-plan`
- `/wsai-implement`
- `/wsai-test`
- `/wsai-validate`
- `/wsai-doc`
- `/wsai-git`

Papéis:

- `/wsai` — entrada/orientação do sistema de desenvolvimento.
- `/wsai-run` — orquestrador autónomo do ciclo completo de uma unidade.
- `/wsai-audit` — fotografia do estado real, sem implementação funcional.
- `/wsai-plan` — plano executável da unidade, sem implementação.
- `/wsai-implement` — implementação da unidade aprovada.
- `/wsai-test` — execução/criação de testes e correcção de falhas dentro do âmbito aprovado.
- `/wsai-validate` — gate independente de consolidação; valida sem alterar código funcional.
- `/wsai-doc` — documentação e estado persistente.
- `/wsai-git` — revisão, commit e sincronização.

Regra: `/wsai-run` usa esta mesma família e não pode contornar os gates definidos por `/wsai-validate`. A arquitectura real do código, testes e contratos é a fonte primária; documentação serve para declarar intenção e estado, não para provar implementação.

## Testes

Base de testes configurada com `pytest`. Executar:

```text
py -3.12 -m pytest -v
```

Baseline registada antes desta auditoria: 415 testes aprovados. A alteração de qualidade do Gate deve ser validada novamente no ambiente local antes de aumentar a baseline; o número remoto permanece 415 até essa execução.

## Estado da arquitectura

```text
Foundation             ████████░░ 80%
Platform               ████████░░ 80%
Hardware Intelligence  ██████████ 100%
Runtime Intelligence   ██████████ 100%
Capability Engine      ██████████ 100%
Model Intelligence     ██████████ 100%
Provider Layer         ██████████ 100%
Task Intelligence      ██████████ 100%
Runtime Engine         █████████░ 99%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies), 8.5 (Runtime Engine), 8.6 (Lifecycle + Compatibility), 8.7 (Architecture Contract Tests), 8.8 (Security/Policy + Project Isolation), 8.9 (Gate — Core pronto para addons) e nos residuais Via B 1 (Monitorização contínua — BASE-34) e 2 (Concorrência entre planos — BASE-35). A auditoria actual detectou uma fragilidade de qualidade no teste de negação do Gate e corrigiu-a para injectar efectivamente o `step_runner`, tornando a asserção `executado == []` observável. Esta correcção ainda requer execução local da suíte para fechar a validação final.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A **decisão material pós-Gate** está registada: **Via B** — fechar primeiro os residuais da Fase 8 (monitorização ✓; concorrência ✓; filas multicamadas) e só depois iniciar a Fase 9 — Knowledge Engine. A próxima unidade de código é a **filas multicamadas** (residual 3, o último da Fase 8), mas deve passar pelo ciclo audit → plan → implement → test → validate → doc → git.
