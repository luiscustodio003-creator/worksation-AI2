# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1, 8.2, 8.3, 8.4 e 8.5 concluídas)

## Base actual

Fase 8.5 — Runtime Engine **CONCLUÍDA**: subsistema `wsai2.runtime_engine` com `RuntimeManager` (consome o `ExecutionPlan` da Fase 7, executa-o com `execute_with_policies` da 8.4 e a governação de recursos da 8.3, devolvendo um `ExecutionReport` com observabilidade por passo) e `Scheduler` (agendamento determinístico por prioridade, estável, com relatório agregado).

## Última unidade concluída

Fase 8.5 — Runtime Engine: `RuntimeManager` valida a executabilidade do plano, constrói o contexto por omissão, executa o plano como unidade de políticas (checkpoint → timeout → recuperação → orçamento) e devolve `ExecutionReport` mesmo em falha (estado global + `StepOutcome` por passo, com `SKIPPED` após a primeira falha e erros normalizados na taxonomia 8.2); `Scheduler` ordena por prioridade (crítica→baixa, estável) e suporta `stop_on_failure`.

## Próxima unidade

Iniciar a **Fase 8.6 — Lifecycle + Compatibility** (hardening 02 e 08): auditá-la e evoluir `wsai2.extension.lifecycle` existente, amarrando o estado de execução das extensões (`ExtensionLifecycleState` da 8.1) ao `RuntimeStatus` do registo (8.1) e adicionando versioning/compatibilidade de contratos antes da execução. Concorrência entre planos, filas multicamadas e monitorização contínua permanecem para unidades posteriores.

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

Baseline registada: 314 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine).

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
Runtime Engine         █████░░░░░ 50%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies) e 8.5 (Runtime Engine), aditivas e reversíveis. A próxima unidade (8.6) trata domínio de lifecycle e compatibilidade, já esboçado na 8.1/8.2.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A próxima unidade da Fase 8 é a **Fase 8.6 — Lifecycle + Compatibility**.
