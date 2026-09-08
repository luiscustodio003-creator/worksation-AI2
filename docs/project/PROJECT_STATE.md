# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1 a 8.8 concluídas — pré-requisitos do Gate cumpridos)

## Base actual

Fase 8.8 — Security/Policy + Project Isolation **CONCLUÍDA**: novo subsistema folha `wsai2.security` (hardening 09 + 10) — `PolicyEngine` com decisão **exact-match por acção** sobre `Principal`/`PolicyDecision`, guardas `require_project`/`assert_same_project` com emissão de `PermissionError`/`ProjectIsolationError`, e enforcement opcional no `RuntimeManager.execute_plan` (decisão antes do passo 1; negação = report `FAILED` com os passos `SKIPPED`). `ExecutionContext.principal` aditivo (default `""`). `FRONTEIRAS` da 8.7 cresceram com (`security`,`core`) e (`runtime_engine`,`security`).

## Última unidade concluída

Fase 8.8 — Security/Policy + Project Isolation: a cadeia `principal -> project -> action -> policy -> decision` com negação por omissão; a taxonomia `PermissionError`/`ProjectIsolationError` da 8.2 ganha emissores reais; sem política fornecida o gestor preserva o comportamento anterior (regressão intacta). Baseline de testes sobe para 387.

## Próxima unidade

**Gate — Core pronto para addons** (formalização): validar a base completa, confirmar os pré-requisitos (contratos, lifecycle, recursos, cancelamento, compatibilidade, segurança, isolamento) com a cobertura de testes existente, e decidir onde a política real é instituída e como `permissions` do `ExtensionContract` alimentam o `PolicyEngine`. Concorrência entre planos, filas multicamadas e monitorização contínua permanecem para unidades posteriores; a Fase 9 — Knowledge Engine arranca depois do Gate.

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
- Extension Lifecycle + Compatibility (máquina de lifecycle, registo e versioning de contratos `wsai2.extension` — Fase 8.6)
- Architecture Contract Tests (regras da Constituição executáveis — Fase 8.7)
- Security / Policy + Project Isolation (política exact-match e fronteira de projectos `wsai2.security` — Fase 8.8)

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

Baseline registada: 387 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine + 40 lifecycle/compatibilidade + 10 contrato arquitectural + 23 security/isolamento).

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
Runtime Engine         █████████░ 95%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies), 8.5 (Runtime Engine), 8.6 (Lifecycle + Compatibility), 8.7 (Architecture Contract Tests) e 8.8 (Security/Policy + Project Isolation), aditivas e reversíveis. Todos os pré-requisitos do Gate de addons têm cobertura de testes.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A próxima unidade da Fase 8 é o **Gate — Core pronto para addons** (formalização da base + decisão de instituição da política real).
