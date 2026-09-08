# WORKSTATION AI 2 — RELATÓRIO DA BASE: EXECUTION CONTEXT + ERROR MODEL

## O que foi feito

Foi criada a fundação transversal de execução da Fase 8: a **taxonomia
unificada de erros** (hardening 03 do CORE_HARDENING_PLAN) e o
**ExecutionContext** com cancelamento cooperativo (hardening 04), num
novo submódulo folha `wsai2.core`. Unidade **Fase 8.2**.

Não foi implementada lógica de execução, scheduler, governação efectiva
de recursos nem políticas de timeout/threads — apenas contratos
declarativos e transporte consistente de dados de execução.

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8), etapas 8.2 do
  CORE_HARDENING_PLAN (hardening 03 e 04).
- `wsai2.core` é uma camada **folha** do núcleo (constituição, artigo 2):
  consumida transversalmente por qualquer subsistema, sem acoplar as
  Fases 1–7 a esta unidade.
- O `Runtime Manager` (8.5) consumirá o `ExecutionContext` para executar
  planos; a governação real de timeout/cancelamento/recuperação é 8.4.

## Para que serve

- **Error Model:** dar um `code` estável e `details` opacos a cada falha,
  cobrindo as categorias em falta na base (Execution, Timeout,
  Cancellation, Resource, Permission, ProjectIsolation) — condição do
  hardening 03 verificada na auditoria.
- **ExecutionContext:** transportar de forma consistente `execution_id`,
  `task_id`, `project_id`, deadline (em `time.monotonic()`), token de
  cancelamento cooperativo, budget de recursos e prioridade.
- **CancellationToken:** cancelamento **cooperativo** e thread-agnostic —
  regista o pedido e valida-o nos pontos de cancelamento; não gere threads.

## Ficheiros criados/alterados

- `src/wsai2/core/__init__.py` — exports públicos do núcleo
- `src/wsai2/core/errors.py` — `WsaiError` + 10 categorias (Validation,
  Capability, Model, Provider, Resource, Timeout, Cancellation,
  Permission, ProjectIsolation, Execution)
- `src/wsai2/core/context.py` — `ExecutionContext`, `CancellationToken`,
  `ExecutionPriority`
- `tests/test_core_errors.py` — 7 testes
- `tests/test_execution_context.py` — 15 testes
- `docs/core/BASE-26-execution-context-error-model.md` — este relatório

Nenhum módulo existente das Fases 1–7 foi alterado.

## Dependências

- `errors.py`: apenas stdlib (`__future__`, nenhuma dependência externa).
- `context.py`: `wsai2.core.errors` (CancellationError, ValidationError),
  stdlib (`dataclasses`, `enum`, `time`, `typing`).
- A referência a `ResourceLimit` (`wsai2.extension`, 8.1) é **apenas
  tipográfica** (`TYPE_CHECKING`): o núcleo permanece folha em runtime.

## Decisões arquitecturais registadas

1. **Núcleo como folha em runtime** (`TYPE_CHECKING` para `ResourceLimit`):
   evita uma dependência circular futura quando a extensão adoptar a
   taxonomia de erros do core (`wsai2.extension → wsai2.core`). O budget
   do contexto reutiliza o contrato `ResourceLimit` sem duplicá-lo nem
   acoplá-lo em runtime.
2. **Erros existentes intactos:** `AdapterError` (`provider/adapters.py`) e
   `ProviderProbeError` (`provider/probes.py`) não foram alterados. O
   alinhamento aditivo do `AdapterError` sobre `ProviderError` fica para
   unidade posterior, após regressão validada (regra de não destruição).
3. **Validação com `ValidationError`:** os novos contratos usam a
   taxonomia (`ValidationError`) em vez de `ValueError`, sem tocar as
   validações existentes das Fases 1–7.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **243 testes aprovados** (22 core + 12 extension + 39 task +
46 provider + 42 model + 33 capability + 24 runtime + 17 hardware + 5
platform + 3 fundação). Regressão das 221 bases intacta.

Os testes validam:

- herança comum e códigos estáveis da taxaonomia;
- transporte de `code`/`details` e captura com `pytest.raises`;
- contexto válido (todos os campos) e defaults;
- imutabilidade (`frozen`);
- `execution_id`/`task_id` vazios e deadline no passado → `ValidationError`;
- deadline: `has_deadline`, `remaining_seconds`, `is_expired`;
- fluxo completo do `CancellationToken` (cancelar → `CancellationError`);
- delegação do cancelamento no contexto; prioridades previstas;
- budget reutilizando `ResourceLimit` da extensão.

## Estado da fase

**Fase 8 — Runtime Engine — EM CURSO**.

Etapas concluídas:

- 8.0 baseline e auditoria ✓
- 8.1 contratos mínimos — Extension Contract ✓
- 8.2 Execution Context + Error Model ✓ (esta unidade)

Em falta (unidades posteriores): Resource Governance (8.3),
timeout/cancellation/recovery (8.4), Runtime Manager + scheduler (8.5),
lifecycle + compatibilidade (8.6), testes de contrato arquitectural
(8.7).

## Riscos residuais

- O cancelamento é cooperativo e não bloqueante; a governação real de
  timeout e threads pertence a 8.4.
- `TimeoutError` e `PermissionError` são tipos próprios de `wsai2.core`
  (não os builtins); não colidem com os `except` existentes porque os
  módulos das Fases 1–7 não os importam.
- O `budget` é declarativo e não é ainda governado (8.3).
- Não existe ainda ligação `ExecutionContext ↔` plano/execução real (8.5).

## Próximo passo

Fase 8.3 — **Resource Governance**: evoluir a gestão de memória existente
(Runtime Intelligence) para governação de recursos (CPU, RAM, GPU/VRAM,
armazenamento/I/O, tempo), sem duplicar mecanismos.