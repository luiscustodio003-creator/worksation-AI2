# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1 a 8.9 concluídas — Gate de addons aprovado; residual Via B em curso — monitorização contínua concluída, concorrência e filas pendentes)

## Base actual

Unidade residual 1 da Fase 8 (Via B) — **Monitorização contínua CONCLUÍDA**: novo módulo `wsai2.runtime_engine.monitoring` (`ExecutionMonitor` thread-safe com hooks de arranque/passo/finalização e `snapshot()`; `ExecutionSnapshot` e `MonitorSnapshot` como API pública). `RuntimeManager.execute_plan` e `Scheduler.run` ganham o kwarg aditivo e reversível `monitor` (execuções negadas pela política também finalizadas; passos `SKIPPED` registados). Baseline sobe para 405 (397 + 8 em `tests/test_runtime_engine_monitoring.py`). `FRONTEIRAS` intactas; nível de medição de recursos do sistema permanece no Runtime Intelligence.

## Última unidade concluída

Fase 8 — residual 1: **Monitorização contínua** (relatório `docs/runtime_engine/BASE-34-runtime-engine-monitoring.md`). Aditiva ao relatório pós-facto da 8.5; observa execuções em curso, marcos do scheduler e negações por política, sem alterar a forma dos relatórios finais nem o determinismo do scheduler por omissão. Baseline de testes: 405.

## Próxima unidade

Implementar a **unidade 2 dos residuais da Fase 8 — Concorrência entre planos**: execução paralela no scheduler, opcional e aditiva, reutilizando o `ExecutionMonitor` e preservando o scheduler determinístico por omissão. A **decisão material pós-Gate** fica registada neste documento (Via B: fechar primeiro os residuais do Runtime — monitorização ✓, concorrência, filas multicamadas); a **Fase 9 — Knowledge Engine** só é iniciada depois do fecho da Fase 8.

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
- Extension Lifecycle + Compatibility (máquina de lifecycle, registo e versioning de contratos `wsai2.extension` — Fase 8.6)
- Architecture Contract Tests (regras da Constituição executáveis — Fase 8.7)
- Security / Policy + Project Isolation (política exact-match e fronteira de projectos `wsai2.security` — Fase 8.8)
- Gate — Core pronto para addons (formalização do marco: critério executável + propagação da política no `Scheduler` + ponte `permissions`→grants no registo — Fase 8.9)

## Desenvolvimento controlado

A base de desenvolvimento está agora formalizada em `docs/project/CONTROLLED_DEVELOPMENT.md` e `docs/architecture/CORE_HARDENING_PLAN.md`.

A família de comandos OpenCode disponível no projecto é:

- `/wsai`
- `/wsai-run`
- `/wsai-audit`
- `/wsai-plan`
- `/wsai-implement`
- `/wsai-test`
- `/wsai-doc`
- `/wsai-git`

`/wsai-run` permanece o orquestrador autónomo. Os restantes comandos permitem executar cada etapa individualmente.

## Testes

Base de testes configurada com `pytest`. Executar:

```text
py -3.12 -m pytest -v
```

Baseline registada: 405 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine + 40 lifecycle/compatibilidade + 10 contrato arquitectural + 23 security/isolamento + 7 gate + 3 ponte no registo + 8 monitorização do runtime).

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
Runtime Engine         █████████░ 97%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies), 8.5 (Runtime Engine), 8.6 (Lifecycle + Compatibility), 8.7 (Architecture Contract Tests), 8.8 (Security/Policy + Project Isolation), 8.9 (Gate — Core pronto para addons) e no residual Via B 1 (Monitorização contínua — BASE-34). O Gate está aprovado com critério executável; os pré-requisitos de addons têm cobertura de testes. A unidade da monitorização está implementada, validada (405) e documentada; o fecho do commit é consolidado nesta corrente de trabalho.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A **decisão material pós-Gate** está registada: **Via B** — fechar primeiro os residuais da Fase 8 (monitorização ✓; em seguida concorrência entre planos e filas multicamadas) e só depois iniciar a Fase 9 — Knowledge Engine. A próxima unidade de código é a **concorrência entre planos**.
