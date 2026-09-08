# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

EM CURSO (Fase 8.1, 8.2, 8.3, 8.4, 8.5 e 8.6 concluídas)

## Base actual

Fase 8.6 — Extension Lifecycle + Compatibility **CONCLUÍDA**: subsistema `wsai2.extension` estendido com `versioning` (leitura semântica de `contract_version` `major.minor`; compatibilidade = mesmo major; rejeição antes do registo — hardening 08), `lifecycle` (máquina de transições do diagrama do hardening 02, pura e sem efeitos laterais) e `registry` (`ExtensionRegistry` no padrão das Fases 4–6, com barreiras de unicidade, compatibilidade e estado `VALIDATED` antes do registo; estado de lifecycle mantido no próprio contrato).

## Última unidade concluída

Fase 8.6 — Lifecycle + Compatibility: `ContractVersion.parse`/`is_compatible_with` com `SUPPORTED_CONTRACT_VERSION = "1.0"`; `transition` valida e devolve novo contrato (imutável) e transições inválidas são `ValidationError` `wsai.extension.lifecycle` sem mutar estado global; `ExtensionRegistry.register` rejeita duplicados (`wsai.extension.duplicate`), contratos incompatíveis (`wsai.extension.contract_incompatible`) e versões mal formadas antes de registar. **Correcção registada:** não existe `RuntimeStatus` do registo — o estado de execução de uma extensão é o próprio campo `lifecycle` do `ExtensionContract` (referência inventada anteriormente removida).

## Próxima unidade

**Fase 8.7 — Testes de contrato arquitectural** (hardening 10): testes que verificam as regras da CONSTITUTION/AGENTS no repositório (fronteiras de dependências, ausência de ciclos de import, isolamento de código Windows/Linux, documentação por módulo) — sem decisão arquitectural nova. Concorrência entre planos, filas multicamadas e monitorização contínua permanecem para unidades posteriores.

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

Baseline registada: 354 testes aprovados (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task + 12 extension + 22 core + 21 resource + 28 execution + 22 runtime_engine + 40 lifecycle/compatibilidade).

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
Runtime Engine         ████████░░ 80%
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

Repositório remoto inicializado. A Fase 8 avançou nas unidades 8.1 (Extension Contract), 8.2 (Execution Context + Error Model), 8.3 (Resource Governance), 8.4 (Execution Policies), 8.5 (Runtime Engine) e 8.6 (Lifecycle + Compatibility), aditivas e reversíveis. A próxima unidade (8.7) é de testes de contrato arquitectural.

## Regra de continuação

A próxima execução deve ler este ficheiro antes de seleccionar trabalho novo. A próxima unidade da Fase 8 é a **Fase 8.7 — Testes de contrato arquitectural**.
