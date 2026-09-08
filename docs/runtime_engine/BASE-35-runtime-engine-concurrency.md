# WORKSTATION AI 2 — RELATÓRIO DA BASE: CONCORRÊNCIA ENTRE PLANOS

## Objectivo

Fechar a **unidade 2 dos residuais da Fase 8** (Via B pós-Gate): dar ao
`Scheduler` a capacidade de executar **vários planos em paralelo**, de
forma **aditiva e opcional**, preservando o agendamento sequencial
determinístico por prioridade como comportamento por omissão.

A unidade não muda a semântica de execução de cada plano (continua no
`RuntimeManager`, com as políticas centralizadas da Fase 8 e a
monitorização contínua) — muda apenas **quantos planos** o `Scheduler`
decorre em simultâneo.

## Arquitectura abrangida

- **Fase 8 — Runtime Engine** (subsistema 3.8), unidade residual declarada
  como posterior ao Gate (hardening 07 do CORE_HARDENING_PLAN).
- **`Scheduler.run`** ganha o kwarg `concurrency: int = 1`:
  - `1` (padrão) — caminho históriico sequencial **intacto** (mesmo código,
    mesma ordem, mesmos relatórios);
  - `> 1` — execução paralela num `ThreadPoolExecutor` com
    `max_workers=concurrency`, preservando a ordem de prioridade no
    relatório agregado.
- **`ResourceGovernor`** passa a ser thread-safe (trinco sobre o livro de
  alocações e o contador de sequência) — dependência **necessária** para a
  partilha segura da mesma instância entre planos paralelos. Alteração
  aditiva: semântica e relatórios intactos em execução única.
- Sem arestas novas em `FRONTEIRAS`; o `Scheduler` já dependia do `manager`
  e da `core`. Filas de espera multicamadas continuam posteriores.

## Componentes envolvidos

- `Scheduler.run(..., concurrency: int = 1, step_runner=None)`:
  - `_agendar_sequencial` — caminho histórico extraído (comportamento
    idêntico, agora também com propagação aditiva de `step_runner`);
  - `_agendar_paralelo` — materializa os contextos **no thread principal**
    (execução única, ordem estável), valida a unicidade dos
    `execution_id` (o monitor indexa por eles; duplicações são rejeitadas
    antes de qualquer execução), submete os planos ao pool e recolhe os
    resultados por posição.
- `stop_on_failure` em paralelo: uma falha sinaliza um `threading.Event`;
  os planos ainda **não iniciados** são descartados (não entram no
  relatório); os que já decorrem concluem e são reportados. Em sequencial
  o comportamento é o histórico (paragem imediata).
- `RuntimeManager.execute_plan` inalterado; `ExecutionMonitor` já era
  thread-safe (unidade 1) e observa todas as execuções paralelas.
- `wsai2.resource.governor.ResourceGovernor` — trinco em
  `_committed`/`allocate`/`release`/`outstanding`.

## Dependências

- `scheduler.py` → `base.py` (`StepRunner`), `manager.py`,
  `wsai2.core.context` (`ValidationError`, `ExecutionContext`),
  `wsai2.core.errors` e stdlib (`threading`, `concurrent.futures`).
- `governor.py` → stdlib `threading` (aditivo).
- Precedentes reutilizados: worker thread daemon da 8.4, token de
  cancelamento thread-agnostic da 8.2, monitor thread-safe da unidade 1.
  Nenhuma responsabilidade duplicada — o pool vive **no scheduler**; o
  gestor continua a executar um plano de cada vez.

## Alterações efectuadas

- `src/wsai2/runtime_engine/scheduler.py` — `concurrency` aditivo
  (sequencial por omissão), `_agendar_sequencial`/`_agendar_paralelo`,
  `step_runner` propagado, validação de `execution_id` únicos, evento de
  paragem para `stop_on_failure`.
- `src/wsai2/resource/governor.py` — thread-safety aditiva (trinco).
- `src/wsai2/runtime_engine/__init__.py` — docstring do subsistema.
- `tests/test_runtime_engine_concurrency.py` — suíte nova (10 testes).

## Testes e resultado

```text
py -3.12 -m pytest   →   415 passed
```

(405 da baseline + 10 da concorrência.) A suíte valida: rejeição de
`concurrency` inválido; equivalência `concurrency=1` com o sequencial;
execução de todos os planos com ordem de prioridade preservada;
**sobreposição real** de execuções (barrier: dois planos encontram-se em
threads diferentes); `stop_on_failure` descartando planos ainda não
iniciados (teste determinístico); falha parcial sem paragem; monitor a
observar todas as execuções paralelas; governador partilhado
reservando/libertando sem perdas (8 planos, 4 workers); rejeição de
`execution_id` duplicados; contextos únicos por omissão.

## Riscos residuais

- **Ordem temporal não garantida**: em paralelo, a ordem de conclusão é
  não determinística (o relatório preserva a ordem de prioridade, não o
  instante de fim). Para ordenação temporal estrita, manter
  `concurrency=1`.
- `step_runner` partilhado é invocado de várias threads — deve ser
  thread-safe ou stateless (documentado no PDF de contrato).
- O pool não mata threads "fugitivas" (por design da Fase 8): planos de
  longa duração têm de observar o token/deadline cooperativo.

## Estado actual

Fase 8 — Runtime Engine: **8.1 a 8.9 + residuais 1 (monitorização) e 2
(concorrência) concluídos**. Baseline **415 testes**. Falta o residual 3
(filas multicamadas) para fechar a Fase 8; a Fase 9 — Knowledge Engine
só é iniciada depois.

## Próximo passo

Implementar a **unidade 3 — Filas multicamadas**: filas por prioridade com
preempção/backlog sobre o scheduler actual (aditivo, opcional, preservando
o agendamento directo existente), seguida de testes, relatório `BASE-*` e
validação. A decisão pós-Gate (Via B) está registada no `PROJECT_STATE`.