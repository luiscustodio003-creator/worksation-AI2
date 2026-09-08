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

> **Estado: IMPLEMENTADO na Fase 8.3.** `wsai2.resource` com
> `ResourceGovernor`: normalização por dimensão (RAM, CPU, VRAM, disco),
> validação de folga (`required <= min(capacity, available_now) −
> committed`) e accounting por instância (`allocate`/`release`).
> Dimensões sem leitura de runtime (VRAM em uso, espaço livre de disco)
> governadas pela capacidade estrutural. Nomes não reconhecidos →
> `UNRECOGNIZED`. Gestão de tempo (8.4) e scheduling (8.5) permanecem em
> unidades posteriores.

## Hardening 06 — Timeout / Cancellation / Recovery

Centralizar políticas no Runtime Engine. Addons não devem inventar mecanismos incompatíveis.

> **Estado: IMPLEMENTADO na Fase 8.4.** `wsai2.execution` com política de
> timeout (`TimeoutPolicy`, `DeadlineGuard`, `run_with_timeout` em thread
> daemon), checkpoints de cancelamento/deadline sobre o
> `ExecutionContext` e recuperação (`RecoveryPolicy`, `run_with_recovery`
> com retry opt-in e backoff); `execute_with_policies` compõe
> checkpoint → timeout → recuperação → reserva/libertação de orçamento
> (`ResourceGovernor`, 8.3). Agendamento/filas e gestor de execução
> pertencem ao 8.5.

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

> **Estado: IMPLEMENTADO na Fase 8.5.** `wsai2.runtime_engine` com
> `RuntimeManager` (executa o `ExecutionPlan` do Task Intelligence como
> unidade de políticas — `execute_with_policies` da 8.4 + `ResourceGovernor`
> da 8.3 — devolvendo `ExecutionReport` por passo) e `Scheduler`
> (agendamento determinístico por prioridade com `stop_on_failure`).
> Concorrência entre planos, filas multicamadas e monitorização contínua
> ficam para unidades posteriores; o passo concreto (contacto
> modelo/fornecedor) é um `step_runner` injectado.

## Hardening 08 — Versioning / Compatibility

Introduzir apenas as versões necessárias para Core/API/Capability/Provider/Extension contracts e rejeitar incompatibilidades antes da execução.

> **Estado: IMPLEMENTADO na Fase 8.6 (extensões).** `wsai2.extension.versioning`
> com `ContractVersion` (`major.minor`, a `version` do addon permanece
> opaca) e `SUPPORTED_CONTRACT_VERSION = "1.0"`; compatibilidade = mesmo
> major. `ExtensionRegistry.register` rejeita antes de registar
> (`wsai.extension.contract_version` / `wsai.extension.contract_incompatible`).
> Core/API/Capability/Provider acumulam evolução de unidades passadas e
> futuras de cada subsistema.

## Hardening 09 — Security / Policy

Antes de Code, GitHub, Agents ou MCP, definir principal → project → capability → resource → action → policy → decision.

> **Estado: NÚCLEO IMPLEMENTADO na Fase 8.8.** `wsai2.security` com
> `Principal`/`PolicyDecision`, `PolicyEngine` de decisão **exact-match
> por acção** (negação por omissão, sem RBAC) e `denied_decision`
> (converte a negação no `PermissionError` da 8.2). Enforcement no
> `RuntimeManager.execute_plan` antes do passo 1 (política injectada;
> sem motor, comportamento preservado). A ligação de
> `permissions` do `ExtensionContract` aos grants do motor fica para a
> instituição da política no Gate.

## Hardening 10 — Project Isolation

Propagar `project_id` pelas fronteiras relevantes e impedir acesso cruzado sem autorização explícita.

> **Estado: NÚCLEO IMPLEMENTADO na Fase 8.8.** `wsai2.security.isolation`
> com `require_project` (project_id obrigatório na fronteira) e
> `assert_same_project` (acesso cruzado → `ProjectIsolationError` da
> 8.2, com esperado/actual em `details`). O `ExecutionContext` (8.2) já
> transportava `project_id`; passa também a transportar `principal`
> (aditivo, default vazio) para a política.

## Hardening 11 — Architecture Contract Tests

Transformar regras da Constituição em testes executáveis: dependências, isolamento, compatibilidade, recursos, timeout, cancellation, permissões e falha isolada de addons.

> **Estado: NÚCLEO IMPLEMENTADO na Fase 8.7.** `tests/test_architecture_contract.py`
> executa as regras de dependências (fronteiras autorizadas entre
> subsistemas), isolamento do código de SO, ausência de ciclos em runtime,
> documentação por subsistema e crescimento controlado. As restantes
> regras (compatibilidade, recursos, timeout, cancellation, permissões e
> falha isolada de addons) são já cobertas pelos testes funcionais das
> unidades 8.1–8.6; o Security/Policy (hardening 09) dará origem aos
> testes de permissões antes do Gate de addons.

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
