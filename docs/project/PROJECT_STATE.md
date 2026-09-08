# WORKSTATION AI 2 — PROJECT STATE

## Versão

0.0.1

## Fase actual

**FASE 8 — Runtime Engine**

## Estado da fase

**IMPLEMENTAÇÃO CONCLUÍDA — validação final pendente.** As unidades 8.1–8.9 e os três residuais Via B estão implementados. O residual 3 — filas multicamadas — foi implementado como camada aditiva sobre o Scheduler. O fecho formal requer execução da suíte completa e `/wsai-validate foundation`.

## Última unidade implementada

Fase 8 — residual 3: **Filas multicamadas** (`BASE-36-runtime-engine-queues.md`). Foi criado `MultilayerExecutionQueue`, com camada pronta por prioridade, backlog, capacidade opcional, preempção apenas de trabalho pendente, promoção do backlog, snapshot/pending/clear e integração opt-in no `Scheduler.run(queue=...)`. A via directa (`queue=None`) mantém o comportamento histórico.

## Estado dos residuais Via B

- Residual 1 — monitorização contínua: **CONCLUÍDO** (`BASE-34`).
- Residual 2 — concorrência entre planos: **CONCLUÍDO** (`BASE-35`).
- Residual 3 — filas multicamadas: **IMPLEMENTADO** (`BASE-36`), validação final pendente.

## Subsistemas funcionais implementados

- Platform Foundation
- Hardware Intelligence
- Runtime Intelligence
- Capability Engine
- Model Intelligence
- Provider Layer
- Task Intelligence
- Extension Contract
- Execution Context + Error Model
- Resource Governance
- Runtime Engine
- Monitorização contínua do Runtime
- Concorrência entre planos
- Filas multicamadas do Runtime: prioridade + backlog + preempção de pendentes
- Extension Lifecycle + Compatibility
- Architecture Contract Tests
- Security / Policy + Project Isolation
- Gate — Core pronto para addons

## Filas multicamadas — contrato

`MultilayerExecutionQueue` é genérica e thread-safe. A prioridade é determinada por `ExecutionPriority` (`CRITICAL`, `HIGH`, `NORMAL`, `LOW`). Com `max_ready=None`, a camada pronta funciona como priority queue. Com capacidade limitada, uma entrada superior pode preemptar a menor prioridade ainda pronta, que passa para o backlog. Nenhum trabalho já iniciado é interrompido.

O Scheduler aceita `queue=None` por omissão. Quando uma fila é fornecida, os planos são admitidos e consumidos pela mesma pipeline de execução, mantendo políticas, monitorização, timeout, recovery, `step_runner` e concorrência existentes.

## Desenvolvimento controlado

A família oficial de comandos OpenCode é:

- `/wsai`
- `/wsai-run`
- `/wsai-audit`
- `/wsai-plan`
- `/wsai-implement`
- `/wsai-test`
- `/wsai-validate`
- `/wsai-doc`
- `/wsai-git`

Regra: a arquitectura real do código e testes é a fonte primária; documentação declara intenção/estado mas não substitui execução de testes.

## Testes

Baseline anterior à unidade 3: **415 testes**.

Foram adicionados **8 testes** em `tests/test_runtime_engine_queue.py`, cobrindo a fila e a integração com o Scheduler. A baseline final não é declarada como aprovada até executar:

```text
py -3.12 -m pytest -v
```

e, depois, executar:

```text
/wsai-validate foundation
```

Foi também criado `.github/workflows/tests.yml` para executar a suíte em Python 3.12 no GitHub Actions. O estado das Actions deve ser confirmado antes do fecho formal.

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
Runtime Engine         ██████████ 100% (implementação)
Knowledge Engine       ░░░░░░░░░░ 0%
API                    ░░░░░░░░░░ 0%
UI                     ░░░░░░░░░░ 0%
```

## Estado Git

A implementação do residual 3 foi adicionada directamente ao `main` em commits incrementais. O repositório contém agora o módulo de fila, integração no Scheduler, testes, relatório BASE-36 e pipeline GitHub Actions.

## Regra de continuação

**Não iniciar Fase 9 ainda.** Primeiro executar a validação final da Fase 8:

```text
pytest completo
    ↓
/wsai-validate foundation
    ↓
resolver GAPs materiais, se existirem
    ↓
validar novamente
    ↓
actualizar PROJECT_STATE para FASE 8 CONCLUÍDA
    ↓
commit final
```
