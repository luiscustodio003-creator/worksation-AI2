# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1 a 8.7 concluídas — falta decisão do Gate de addons)

## Base actual

Fase 8.7 — Architecture Contract Tests **CONCLUÍDA**: `tests/test_architecture_contract.py` (10 testes) que executam as regras da CONSTITUTION/AGENTS sobre o repositório — docstrings e bases documentais por subsistema, fronteiras de import autorizadas (`FRONTEIRAS`), isolamento dos adaptadores de SO (acesso só via `get_platform`), ausência de ciclos de import em runtime e proibição de subsistemas/squatters antecipados (api, ui, knowledge). Unidade 100% aditiva, sem tocar em código de produção.

## Última unidade concluída

Fase 8.7 — Architecture Contract Tests: `FRONTEIRAS` (21 arestas autorizadas entre subsistemas, fotografadas por auditoria), parser AST com exclusão de imports tipográficos `TYPE_CHECKING`, detecção de ciclos em runtime, e 10 verificações executáveis (Artigo 2, 4, 8, 10, 13 da Constituição). Baseline de testes sobe para 364.

## Próxima unidade

**Decisão arquitectural material — Security / Policy (hardening 09) e Project Isolation (hardening 10)**, pré-requisitos do Gate de addons: modelar `principal → project → capability → resource → action → policy → decision` e a propagação/preservação de `project_id` nas fronteiras. São responsabilidades ainda sem módulo próprio na Fase 8 — exigem auditoria e planeamento dedicados. Concorrência entre planos, filas multicamadas e monitorização contínua permanecem para unidades posteriores.

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

Baseline registada: 364 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine + 40 lifecycle/compatibilidade + 10 contrato arquitectural).

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
Runtime Engine         █████████░ 90%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies), 8.5 (Runtime Engine), 8.6 (Lifecycle + Compatibility) e 8.7 (Architecture Contract Tests), aditivas e reversíveis. Falta decidir o Security/Policy (hardening 09) e o Project Isolation (hardening 10) antes do Gate de addons.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A próxima unidade da Fase 8 é a **decisão arquitectural material — Security / Policy (hardening 09) e Project Isolation (hardening 10)**, pré-requisitos do Gate de addons.
