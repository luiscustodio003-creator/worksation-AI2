# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1 a 8.9 concluídas — Gate de addons aprovado)

## Base actual

Fase 8.9 — Gate — Core pronto para addons **CONCLUÍDO**: formalização do marco com critério executável em `tests/test_gate_addons.py` (pré-requisitos públicos + integrações de instituição). Integrações aditivas: `Scheduler.run` propaga `policy` ao `RuntimeManager` (contrato de composição — quem cria o runtime passa o motor) e `ExtensionRegistry.register` materializa `permissions` como **grants por id de extensão** (acções exactas) quando um motor é fornecido. `FRONTEIRAS` da 8.7 ganham a aresta (`extension`,`security`). `wsai2.security` permanece folha.

## Última unidade concluída

Fase 8.9 — Gate — Core pronto para addons: a política passa a ser instituída na fila (scheduler), ligada ao contrato (ponte permissions→grants no registo) e verificável (fotografia executável do Gate). Baseline de testes sobe para 397. Concorrência, filas multicamadas e monitorização contínua continuam unidades posteriores — não são pré-requisitos do Gate.

## Próxima unidade

**Decisão material pós-Gate**: avançar para a **Fase 9 — Knowledge Engine** (ingestão, extracção e metadados) ou fechar primeiro as unidades residuais do Runtime (monitorização contínua; depois concorrência e filas multicamadas). Enquanto a decisão não for registada, nenhuma das duas vias deve ser iniciada.

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

Baseline registada: 397 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine + 40 lifecycle/compatibilidade + 10 contrato arquitectural + 23 security/isolamento + 7 gate + 3 ponte no registo).

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

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies), 8.5 (Runtime Engine), 8.6 (Lifecycle + Compatibility), 8.7 (Architecture Contract Tests), 8.8 (Security/Policy + Project Isolation) e 8.9 (Gate — Core pronto para addons), aditivas e reversíveis. O Gate está aprovado com critério executável; os pré-requisitos de addons têm cobertura de testes.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A próxima unidade exige uma **decisão material pós-Gate**: Fase 9 — Knowledge Engine versus unidades residuais do Runtime (monitorização contínua; depois concorrência e filas multicamadas). Até a decisão ser registada, nenhuma das duas vias deve ser iniciada.
