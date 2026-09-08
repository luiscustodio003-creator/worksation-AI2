# WORKSTATION AI 2 — RELATÓRIO DA BASE: MONITORIZAÇÃO CONTÍNUA DO RUNTIME ENGINE

## Objectivo

Fechar a **unidade 1 dos residuais da Fase 8** (Via B pós-Gate): complementar a
observabilidade **pós-facto** da unidade 8.5 (`ExecutionReport`/`SchedulerReport`)
com observação **durante** a execução. O `ExecutionMonitor` regista o estado em
curso de cada execução e de cada agendamento e permite interrogar `snapshot()`
a qualquer momento — de outra thread — sem esperar pelo relatório final.

É uma unidade **aditiva e reversível**: quando o `RuntimeManager` ou o
`Scheduler` são usados sem `monitor`, o comportamento é exactamente o das
unidades anteriores (regressão intacta).

## Arquitectura abrangida

- **Fase 8 — Runtime Engine** (subsistema 3.8), unidade residual declarada como
  posterior ao Gate (hardening 07 do CORE_HARDENING_PLAN).
- Toda a alteração permanece **dentro de `wsai2.runtime_engine`** — nenhuma
  aresta nova em `FRONTEIRAS`; `monitoring.py` importa apenas do próprio
  subsistema (`base.py`) e da biblioteca padrão (`threading`, `time`).
- Fora de âmbito, por fronteira: a medição de recursos do sistema (CPU/RAM/GPU)
  pertence ao Runtime Intelligence (`wsai2.runtime`) e não é observada aqui.

## Componentes envolvidos

- `src/wsai2/runtime_engine/monitoring.py` (novo):
  - `ExecutionMonitor` — colector thread-safe (`threading.Lock`) com hooks
    `on_execution_started` / `on_step_started` / `on_execution_finished` /
    `on_schedule_started` / `on_schedule_finished` e `snapshot()`.
  - `ExecutionSnapshot` — execução em curso: `execution_id`, `task_id`,
    `running`, `started_at`, `elapsed`, `current_step`, `current_step_name`.
  - `MonitorSnapshot` — fotografia global: `running`, `finished`
    (`ExecutionReport`s), `started`, `completed`, `schedule_started_at`,
    `last_schedule` (`SchedulerReport`).
- `RuntimeManager.execute_plan(..., monitor=None)` — hooks de arranque, por
  passo e de finalização (inclui execuções negadas pela política, com passos
  `SKIPPED`).
- `Scheduler.run(..., monitor=None)` — propaga o monitor ao gestor e regista os
  marcos do agendamento.
- `runtime_engine/__init__.py` — novos exports públicos (`ExecutionMonitor`,
  `ExecutionSnapshot`, `MonitorSnapshot`).

## Dependências

- `monitoring.py` → `wsai2.runtime_engine.base` (tipos de relatório) e stdlib.
- Sem dependências novas fora do subsistema; sem ciclos; `FRONTEIRAS` intactas.
- Reutilização (não duplicação): o monitor retém o **próprio** `ExecutionReport`
  produzido pelo gestor e o último `SchedulerReport` — não recria relatórios.
- Precedente de concorrência já aprovado na Fase 8: worker thread daemon da 8.4
  (`execution/runner.py`) e token de cancelamento thread-agnostic da 8.2.

## Alterações efectuadas

- `src/wsai2/runtime_engine/monitoring.py` — novo módulo.
- `src/wsai2/runtime_engine/manager.py` — kwarg `monitor` aditivo + hooks; a
  lista de passos, as políticas e o relatório finais não mudam de forma.
- `src/wsai2/runtime_engine/scheduler.py` — kwarg `monitor` aditivo, propaga ao
  gestor e regista início/fim do agendamento.
- `src/wsai2/runtime_engine/__init__.py` — exports e docstring.
- `tests/test_runtime_engine.py` — fakes de gestor aceitam o kwarg `monitor`
  (compensa a propagação do scheduler).
- `tests/test_runtime_engine_monitoring.py` — suíte nova (8 testes).

## Testes e resultado

```text
py -3.12 -m pytest   →   405 passed
```

(397 da baseline + 8 da monitorização.) A suíte nova valida: API pública;
monitor vazio; execução **in-flight** observada de outra thread (running,
identidade, passo actual, elapsed); avanço entre passos com tempo a decorrer;
falha de passo finalizada e registada; execução negada pela política também
finalizada; reutilização do relatório final; propagação pelo scheduler com a
ordem e o `last_schedule` retidos.

## Riscos residuais

- A monitorização é **pull** via `snapshot()` (sem emissão de eventos/
  callbacks); quando houver necessidade de sinks contínuos, esta API evolui
  sem quebrar o contrato actual.
- Concorrência entre planos e filas multicamadas continuam por implementar —
  são as unidades 2 e 3 dos residuais da Fase 8.
- O observável não mede recursos do sistema (por fronteira arquitectural).

## Estado actual

Fase 8 — Runtime Engine: **8.1 a 8.9 + residual 1 (monitorização contínua)
concluído**. Baseline **405 testes**. Unidades pendentes da Fase 8: concorrência
entre planos (próxima) e filas multicamadas; Fase 9 fica depois do fecho da
Fase 8.

## Próximo passo

Implementar a **unidade 2 — Concorrência entre planos** (scheduler com execução
paralela, opcional e aditiva, preservando o scheduler determinístico por
omissão e reutilizando o `ExecutionMonitor`), seguida de testes, relatório
`BASE-*` e validação. A decisão pós-Gate (Via B: fechar os residuais do Runtime)
é registada no `PROJECT_STATE`.