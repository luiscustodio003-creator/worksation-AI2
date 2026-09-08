# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1, 8.2, 8.3 e 8.4 concluídas)

## Base actual

Fase 8.4 — Execution Policies **CONCLUÍDA**: subsistema `wsai2.execution` com políticas centrais de timeout (`TimeoutPolicy`+`DeadlineGuard`+`run_with_timeout`), cancelamento cooperativo (checkpoints sobre `ExecutionContext`/`CancellationToken`) e recuperação (`RecoveryPolicy`+`run_with_recovery`), compostas em `execute_with_policies` com reserva/libertação de recursos no `ResourceGovernor`.

## Última unidade concluída

Fase 8.4 — Execution Policies: política de timeout com deadline efectiva = a mais curta (política vs contexto), guard monotónico injectável e thread worker daemon; checkpoints de cancelamento/deadline; retry opt-in com backoff e último erro preservado; `execute_with_policies` compõe checkpoint→timeout→recuperação→orçamento (libertação em `finally`).

## Próxima unidade

Iniciar a **Fase 8.5 — Runtime Manager + Scheduler**: consumir o `ExecutionPlan` (Fase 7), lançar execuções com `execute_with_policies`, gerir filas, prioridades e o ciclo de vida das execuções — passo que introduz uma decisão arquitectural material (gestor central de execução) e requer planeamento dedicado.

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
- Execution Policies (timeout, cancelamento cooperativo e recuperação `wsai2.execution` — Fase 8.4)

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

Baseline registada: 292 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution).

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
Runtime Engine         ░░░░░░░░░░ 0%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance) e 8.4 (Execution Policies), aditivas e reversíveis. A próxima unidade (8.5) introduz o gestor de execução e o scheduler — decisão arquitectural material a planear dedicadamente.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A próxima unidade da Fase 8 é a **Fase 8.5 — Runtime Manager + Scheduler**.
