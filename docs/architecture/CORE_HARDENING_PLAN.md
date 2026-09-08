# WORKSTATION AI 2 — PLANO DE HARDENING DA BASE

## Objectivo

Preparar a base do WSAI 2 para receber addons sem criar uma arquitectura paralela nem alterar destrutivamente os subsistemas já concluídos.

Este documento é um **plano de evolução**. Não declara estes componentes como implementados.

## Regra de entrada

Antes de implementar cada ponto:

```text
AUDITAR → localizar implementação existente → classificar GAP → planear impacto → implementar apenas o necessário
```

## Estado inicial conhecido

| Área | Estado inicial | Regra |
|---|---|---|
| Capability Registry | EXISTENTE | evoluir, não duplicar |
| Provider Registry | EXISTENTE | evoluir, não duplicar |
| Task Intelligence | CONCLUÍDA | não reimplementar |
| Runtime Engine | PRÓXIMA FASE | integrar com Task Intelligence |
| `wsai-run` | EXISTENTE | preservar autonomia e observabilidade |
| comandos OpenCode | `/wsai-run` existente | expandir para comandos individuais |

## Hardening 01 — Extension Contract

Definir o contrato mínimo comum para extensões/addons: identidade, versão, versão do contrato, capacidades, dependências, recursos, permissões e lifecycle.

Não criar um Plugin Manager pesado sem necessidade. O contrato deve integrar-se com Capability Engine, Provider Layer e Runtime Engine.

> **Estado: IMPLEMENTADO na Fase 8.1** (passo 8.1 da ordem recomendada).
> `src/wsai2/extension/base.py` (ExtensionContract, ExtensionKind,
> ExtensionLifecycleState, ResourceLimit), imutável e validado à criação.
> Registo, gestão e lifecycle de execução permanecem em unidades posteriores.

## Hardening 02 — Lifecycle

Estados previstos:

```text
DISCOVERED → VALIDATED → REGISTERED → INITIALIZING → READY
                                      ↓
                                  RUNNING
                                      ↓
                             DEGRADED / FAILED
                                      ↓
                              STOPPING → STOPPED
```

Falha de addon não pode derrubar o Core.

## Hardening 03 — Unified Error Model

Criar uma taxonomia transversal apenas quando a auditoria mostrar que as excepções actuais não cobrem o contrato necessário.

Exemplos: Validation, Capability, Model, Provider, Resource, Timeout, Cancellation, Permission, ProjectIsolation e Execution.

> **Estado: IMPLEMENTADO na Fase 8.2.** `wsai2.core.errors` com `WsaiError`
> (code + details) e 10 categorias. O alinhamento aditivo do
> `AdapterError`/`ProviderProbeError` sobre a taxaonomia fica para unidade
> posterior, após regressão validada (regra de não destruição).

## Hardening 04 — Execution Context

Transportar de forma consistente `execution_id`, `task_id`, `project_id`, deadline, cancellation token, resource budget, prioridade e metadata.

> **Estado: NÚCLEO IMPLEMENTADO na Fase 8.2.** `wsai2.core.context` com
> `ExecutionContext` imutável e validado, `CancellationToken` cooperativo
> (thread-agnostic) e `ExecutionPriority`. A governação efectiva de
> timeout/cancelamento/recuperação permanece na 8.4.

## Hardening 05 — Resource Governance

Evoluir a gestão de memória existente para governação de recursos, sem duplicar mecanismos:

- CPU;
- RAM;
- GPU/VRAM;
- armazenamento/I/O;
- threads/processos;
- contexto/KV cache quando aplicável;
- tempo de execução.

## Hardening 06 — Timeout / Cancellation / Recovery

Centralizar políticas no Runtime Engine. Addons não devem inventar mecanismos incompatíveis.

## Hardening 07 — Scheduler / Runtime Manager

Implementar a Fase 8 sobre o plano de execução já produzido pela Fase 7:

```text
Task Intelligence
      ↓
ExecutionPlan
      ↓
Runtime Engine
      ↓
Resource Governance
      ↓
Provider / Model Runtime
      ↓
Execution Result
```

## Hardening 08 — Versioning / Compatibility

Introduzir apenas as versões necessárias para Core/API/Capability/Provider/Extension contracts e rejeitar incompatibilidades antes da execução.

## Hardening 09 — Security / Policy

Antes de Code, GitHub, Agents ou MCP, definir principal → project → capability → resource → action → policy → decision.

## Hardening 10 — Project Isolation

Propagar `project_id` pelas fronteiras relevantes e impedir acesso cruzado sem autorização explícita.

## Hardening 11 — Architecture Contract Tests

Transformar regras da Constituição em testes executáveis: dependências, isolamento, compatibilidade, recursos, timeout, cancellation, permissões e falha isolada de addons.

## Ordem recomendada

```text
Fase 8.0 — Baseline e auditoria
       ↓
Fase 8.1 — contratos mínimos
       ↓
Fase 8.2 — Execution Context + Error Model
       ↓
Fase 8.3 — Resource Governance
       ↓
Fase 8.4 — timeout + cancellation + recovery
       ↓
Fase 8.5 — Runtime Manager + scheduler
       ↓
Fase 8.6 — lifecycle + compatibility
       ↓
Fase 8.7 — testes de contrato arquitectural
       ↓
Gate — Core pronto para addons
```

Security e Project Isolation devem ser concluídos antes de activar addons com acesso a código, ficheiros externos, GitHub, agentes ou MCP.

## Gate de addons

Nenhum addon de grande impacto deve ser considerado pronto apenas porque o seu módulo funciona isoladamente. O Core deve primeiro garantir contratos, lifecycle, execução, recursos, cancelamento, compatibilidade, segurança e isolamento suficientes para o tipo de addon.
