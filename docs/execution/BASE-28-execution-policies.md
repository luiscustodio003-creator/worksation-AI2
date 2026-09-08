# WORKSTATION AI 2 — RELATÓRIO DA BASE: EXECUTION POLICIES

## O que foi feito

Foi criada a camada de **políticas de execução** da Fase 8 (hardening 06
do CORE_HARDENING_PLAN) num novo subsistema **`wsai2.execution`**:
enforcement de **timeout**, **cancelamento cooperativo** (checkpoints) e
**recuperação** (retry), centralizados no Runtime Engine para que os
addons não inventem mecanismos incompatíveis. Unidade **Fase 8.4**.

Não foi implementado agendamento, fila de tarefas nem gestor de execução
— isso pertence à unidade 8.5. As políticas compõem-se sobre o que já
existe: `ExecutionContext`/`CancellationToken` (8.2), `ResourceGovernor`
(8.3), taxonomia de erros (8.2).

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8), etapa 8.4 do
  CORE_HARDENING_PLAN (hardening 06).
- `wsai2.execution` é um subsistema **folha** consumível pelo futuro
  `Runtime Manager` (8.5); o núcleo `wsai2.core` permanece folha — a
  gestão de threads e relógios de enforcement fica **fora** do núcleo,
  nesta camada de políticas.
- O fluxo do hardening 07 passa por aqui: o Runtime Manager executará
  usando `execute_with_policies` (reserva de recursos + timeout +
  cancelamento + recuperação) sobre o `ExecutionPlan` da Fase 7.

## Para que serve

- **Timeout:** `TimeoutPolicy` (duração ou deadline absoluta em
  `time.monotonic`), `DeadlineGuard` (relógio monotónico injectável) e
  `run_with_timeout` (execução em *thread worker* daemon com `join` por
  limite; sem limite, corre no thread actual sem sobrecarga).
- **Cancelamento:** checkpoints (`_checkpoint`) que validam o token
  cooperativo e a deadline do `ExecutionContext` nos pontos de controlo —
  levantam `CancellationError`/`TimeoutError` antes e entre tentativas.
- **Recuperação:** `RecoveryPolicy` (máx. tentativas, atraso base, factor
  de backoff, tipos de erro repetíveis) e `run_with_recovery`; no fim,
  o último erro é re-lançado preservando o tipo original.
- **Composição centralizada:** `execute_with_policies` aplica, por ordem:
  checkpoint inicial → timeout efectivo (política e/ou deadline do
  contexto, o mais curto) → recuperação → reserva e libertação do
  orçamento no `ResourceGovernor` (`finally`).

## Ficheiros criados/alterados

- `src/wsai2/execution/base.py` — contratos: `TimeoutPolicy`,
  `RecoveryPolicy`, `RetryAttempt` (declarativos, sem execução)
- `src/wsai2/execution/runner.py` — `DeadlineGuard`, `run_with_timeout`,
  `run_with_recovery`, `execute_with_policies`
- `src/wsai2/execution/__init__.py` — exports públicos do submódulo
- `tests/test_execution_policies.py` — 28 testes
- `docs/execution/BASE-28-execution-policies.md` — este relatório

Nenhum módulo existente das Fases 1–7 nem da 8.1–8.3 foi alterado.

## Dependências

- `base.py`: stdlib (`dataclasses`, `enum` — este último não usado,
  removido) e `wsai2.core.errors` (`ValidationError`).
- `runner.py`: `wsai2.core.context` (`ExecutionContext`), `wsai2.core.errors`
  (`TimeoutError`) e `wsai2.execution.base`. O `ResourceGovernor` e o
  `ResourceAllocation` são referências **tipográficas** (`TYPE_CHECKING`).
- Direcção das dependências: `execution` aponta para dentro (core,
  resource); não é consumido por nenhum subsistema fora do Runtime Engine
  até ao `Runtime Manager` (8.5).

## Decisões arquitecturais registadas

1. **Políticas fora do núcleo:** o token cooperativo (8.2) é
   thread-agnostic por desenho; as threads de enforcement e os relógios
   pertencem à camada de políticas (`execution`), respeitando a folha do
   `core`.
2. **Thread daemon, nunca morte de thread:** uma execução que ignore a
   deadline não é terminada à força (inseguro e não portátil); o
   `TimeoutError` é levantado no chamador e o código cooperativo deve
   observar token/deadline para terminar. Limitação documentada.
3. **Erro original preservado:** `run_with_recovery` re-lança **o último
   erro** com o tipo original (capturável com `pytest.raises`), em vez de
   embrulhar em excepção genérica; `run_with_timeout` propaga erros de
   `fn` tal e qual.
4. **Retry opt-in:** `retry_error_types` é vazio por omissão — sem
   repetição automática; evita repetir falhas por engano e torna a política
   explicitamente declarada.
5. **Deadline efectiva = a mais curta** entre a política e o contexto
   (`_resolve_deadline`), mantendo coerência com o `ExecutionContext`.
6. **Relógios e espera injectáveis** (`clock`, `sleeper`) para testes
   determinísticos e rápidos, sem falsa dependência do relógio real.
7. **Recursos em `finally`:** a reserva do `ResourceGovernor` é sempre
   libertada, mesmo em erro de execução.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **292 testes aprovados** (28 execution + 21 resource + 22 core
+ 12 extension + 39 task + 46 provider + 42 model + 33 capability + 24
runtime + 17 hardware + 5 platform + 3 fundação). Regressão dos 264
anteriores intacta — alteração 100% aditiva.

Os 28 testes validam:

- `TimeoutPolicy`: ilimitada por omissão, duração→deadline, deadlines
  rejeitadas duplas/negativas (`ValidationError`);
- `DeadlineGuard`: tempo restante, expiração, `TimeoutError` com código
  `wsai.timeout.exceeded`;
- `run_with_timeout`: sem limite (directo), com limite (thread +
  resultado), timeout excedido, propagação do erro de `fn`, deadline do
  contexto e cancelamento do contexto;
- `RecoveryPolicy`: defaults, validações, atraso por tentativa com backoff;
- `run_with_recovery`: sucesso em tentativa seguinte, esgotamento com
  último erro preservado, não repetição de erro não declarado, histórico
  de tentativas, `sleeper` chamado com o atraso;
- `execute_with_policies`: execução directa, checkpoint de cancelamento e
  de deadline expirada, timeout da política, recuperação combinada,
  reserva+libertação de recursos e libertação mesmo com erro.

## Estado da fase

**Fase 8 — Runtime Engine — EM CURSO**.

Etapas concluídas:

- 8.0 baseline e auditoria ✓
- 8.1 contratos mínimos — Extension Contract ✓
- 8.2 Execution Context + Error Model ✓
- 8.3 Resource Governance ✓
- 8.4 Execution Policies — timeout + cancelamento + recuperação ✓ (esta unidade)

Em falta (unidades posteriores): Runtime Manager + scheduler (8.5),
lifecycle + compatibilidade (8.6), testes de contrato arquitectural (8.7).

## Riscos residuais

- **Thread daemon em fuga:** código não cooperativo que ignore a deadline
  continua a correr em segundo plano após `TimeoutError` (não é morto);
  o `Runtime Manager` (8.5) deverá lidar com a reutilização/observação
  desses casos.
- **Retry explícito:** erros não declarados em `retry_error_types` não
  são repetidos — as políticas de recuperação "transitórias" terão de ser
  declaradas pelo chamador (política deliberada).
- **Sem agendamento:** não há filas nem priorização; a composição com o
  `ExecutionContext.priority` e o `ExecutionPlan` é trabalho da 8.5.
- As políticas não cobrem ainda o tempo de "preparação" dos addons
  (lifecycle); isso é matéria da 8.6.

## Próximo passo

Fase 8.5 — **Runtime Manager + Scheduler**: consumir o `ExecutionPlan`
(Fase 7), lançar execuções com `execute_with_policies`, gerir filas,
prioridades e a vida das execuções — o passo seguinte introduz uma decisão
arquitectural material (gestor central de execução) e requer planeamento
dedicado.