# WORKSTATION AI 2 — PLANO DE HARDENING DA BASE

## Objectivo

Preparar a base do WSAI 2 para receber addons sem criar uma arquitectura paralela nem alterar destrutivamente os subsistemas já concluídos.

Este documento é um **plano de evolução**. Cada ponto deve ser lido em conjunto com o estado real do código, testes e `PROJECT_STATE.md`.

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

> **Estado: IMPLEMENTADO na Fase 8.6.** `wsai2.extension.lifecycle` com a
> máquina de transições do diagrama (pura: valida e devolve novo contrato
> `frozen`, nunca executa acções de sistema). Transições inválidas são
> `ValidationError` `wsai.extension.lifecycle`, sem mutar estado fora de
> quem invoca — uma transição negada não corrompe o catálogo.

## Hardening 03 — Unified Error Model

Criar uma taxonomia transversal apenas quando a auditoria mostrar que as excepções actuais não cobrem o contrato necessário.

Exemplos: Validation, Capability, Model, Provider, Resource, Timeout, Cancellation, Permission, ProjectIsolation e Execution.

> **Estado: IMPLEMENTADO na Fase 8.2.** `wsai2.core.errors` com `WsaiError`
> (code + details) e 10 categorias. O alinhamento aditivo do
> `AdapterError`/`ProviderProbeError` sobre a taxonomia fica para unidade
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

> **Estado: IMPLEMENTADO na Fase 8.3.** `wsai2.resource` com
> `ResourceGovernor`: normalização por dimensão (RAM, CPU, VRAM, disco),
> validação de folga e accounting por instância (`allocate`/`release`).
> Dimensões sem leitura de runtime são governadas pela capacidade estrutural.
> Nomes não reconhecidos → `UNRECOGNIZED`.

## Hardening 06 — Timeout / Cancellation / Recovery

Centralizar políticas no Runtime Engine. Addons não devem inventar mecanismos incompatíveis.

> **Estado: IMPLEMENTADO na Fase 8.4.** `wsai2.execution` com política de
> timeout, checkpoints de cancelamento/deadline, recuperação com retry opt-in
> e composição das políticas com reserva/libertação de orçamento.

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

> **Estado: IMPLEMENTADO E COMPLETADO NA Fase 8.** `wsai2.runtime_engine`
> fornece `RuntimeManager` e `Scheduler`. Sobre a implementação base foram
> concluídos os três residuais Via B:
>
> 1. **Monitorização contínua** — `ExecutionMonitor`, thread-safe, com
>    `snapshot()` e integração aditiva/reversível (BASE-34).
> 2. **Concorrência entre planos** — `Scheduler.run(concurrency=...)`, com
>    caminho sequencial preservado por omissão, execução paralela opcional e
>    `ResourceGovernor` thread-safe (BASE-35).
> 3. **Filas multicamadas** — `MultilayerExecutionQueue`, com prioridades
>    `CRITICAL/HIGH/NORMAL/LOW`, backlog, capacidade opcional, preempção apenas
>    de trabalho pendente, promoção do backlog, ordenação determinística,
>    `snapshot()`/`pending()`/`clear()` e integração opt-in em
>    `Scheduler.run(queue=...)` (BASE-36).
>
> A fila é uma camada aditiva: `queue=None` mantém o caminho directo histórico.
> Nenhum trabalho já iniciado é interrompido por preempção.

## Hardening 08 — Versioning / Compatibility

Introduzir apenas as versões necessárias para Core/API/Capability/Provider/Extension contracts e rejeitar incompatibilidades antes da execução.

> **Estado: IMPLEMENTADO na Fase 8.6 (extensões).** `wsai2.extension.versioning`
> com `ContractVersion` (`major.minor`), compatibilidade por major e rejeição
> antes do registo/execução. Core/API/Capability/Provider acumulam evolução
> futura conforme cada subsistema avançar.

## Hardening 09 — Security / Policy

Antes de Code, GitHub, Agents ou MCP, definir principal → project → capability → resource → action → policy → decision.

> **Estado: NÚCLEO IMPLEMENTADO na Fase 8.8; PONTE no Gate (8.9).**
> `wsai2.security` implementa `PolicyEngine` exact-match por acção,
> `denied_decision`, enforcement no `RuntimeManager` e propagação pelo
> `Scheduler`. O `ExtensionRegistry` materializa `permissions` como grants
> por id de extensão.

## Hardening 10 — Project Isolation

Propagar `project_id` pelas fronteiras relevantes e impedir acesso cruzado sem autorização explícita.

> **Estado: NÚCLEO IMPLEMENTADO na Fase 8.8.** `wsai2.security.isolation`
> fornece `require_project` e `assert_same_project`, com
> `ProjectIsolationError`. O `ExecutionContext` transporta `project_id` e,
> de forma aditiva, `principal`.

## Hardening 11 — Architecture Contract Tests

Transformar regras da Constituição em testes executáveis: dependências, isolamento, compatibilidade, recursos, timeout, cancellation, permissões e falha isolada de addons.

> **Estado: IMPLEMENTADO na Fase 8.7 e reforçado nas unidades posteriores.**
> `tests/test_architecture_contract.py` executa as regras de dependências,
> isolamento do código de SO, ausência de ciclos de import e documentação por
> subsistema. As restantes regras são cobertas pelos testes funcionais das
> unidades 8.1–8.9 e pelos residuais Via B.

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
Fase 8.8 — Security / Project Isolation
       ↓
Fase 8.9 — Gate — Core pronto para addons
       ↓
Residual Via B 1 — monitorização
       ↓
Residual Via B 2 — concorrência
       ↓
Residual Via B 3 — filas multicamadas
       ↓
Validação final da Fundação
       ↓
Fase 9 — Knowledge Engine
```

A ordem concreta dos residuais Via B é governada por `PROJECT_STATE.md` e deve ser alterada apenas perante uma nova decisão arquitectural explícita. Não se deve reimplementar uma responsabilidade já concluída.

Security e Project Isolation devem ser concluídos antes de activar addons com acesso a código, ficheiros externos, GitHub, agentes ou MCP.

## Gate de addons

Nenhum addon de grande impacto deve ser considerado pronto apenas porque o seu módulo funciona isoladamente. O Core deve primeiro garantir contratos, lifecycle, execução, recursos, cancelamento, compatibilidade, segurança e isolamento suficientes para o tipo de addon.

> **Estado: GATE APROVADO na Fase 8.9.** O marco foi formalizado com um
> critério executável — `tests/test_gate_addons.py`: fotografia dos
> pré-requisitos públicos e das integrações de instituição. O Gate foi
> seguido, por decisão Via B documentada, pelos residuais de monitorização,
> concorrência e filas multicamadas. Esses residuais completam o Runtime
> Engine, mas não alteram retroactivamente o critério do Gate 8.9.
