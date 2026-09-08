# WORKSTATION AI 2 — RELATÓRIO DA BASE: RUNTIME ENGINE

## O que foi feito

Foi criado o **Runtime Engine executável** da Fase 8 (hardening 07 do
CORE_HARDENING_PLAN) num novo subsistema **`wsai2.runtime_engine`**:
o **`RuntimeManager`** (gestor de execução) consome o `ExecutionPlan`
produzido pelo Task Intelligence (Fase 7), executa os seus passos com as
políticas centralizadas (timeout, cancelamento cooperativo e recuperação
da Fase 8.4) e a governação de recursos (Fase 8.3), produzindo um
**`ExecutionReport`** com observabilidade por passo; o **`Scheduler`**
agenda múltiplos planos por prioridade de forma determinística e devolve
um relatório agregado (`SchedulerReport`). Unidade **Fase 8.5**.

O scheduler desta unidade é **sequencial por plano**: decide a ordem
(prioridade, estável) e executa um de cada vez. Concorrência entre planos
e filas multicamadas permanecem para unidade posterior (não anunciadas).

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8), ponto "Scheduler /
  Runtime Manager" do CORE_HARDENING_PLAN (hardening 07).
- Fecha o fluxo do hardening 07:
  `Task Intelligence → ExecutionPlan → Runtime Engine → Resource
  Governance → Provider/Model Runtime → Execution Result`.
- `wsai2.runtime_engine` **consome** `wsai2.task` (o `ExecutionPlan`),
  `wsai2.execution` (`execute_with_policies`, 8.4), `wsai2.resource` (o
  `ResourceGovernor`, 8.3, injectado) e `wsai2.core` (contexto,
  prioridade, taxonomia de erros). **Não** conhece fornecedores nem
  modelos: a realização de cada passo é um `step_runner` injectado.
- Nomenclatura: **`runtime_engine`** distingue-se de `wsai2.runtime`
  (Runtime Intelligence, Fase 3 — que mede o estado); este subsistema
  executa planos. Fora de âmbito: lifecycle de extensões (8.6),
  compatibilidade/versioning (8.6) e testes de contrato (8.7).

## Para que serve

- **Executar planos** do Task Intelligence (ex.: toda a pipeline
  requisitos → capacidades → modelo → fornecedor já planeada na Fase 7),
  aplicando as políticas centrais a **todo o plano como unidade**.
- **Governar recursos**: o orçamento do `ExecutionContext.budget` é
  reservado no `ResourceGovernor` durante a execução e libertado em
  `finally` (via `execute_with_policies` da 8.4).
- **Observar cada passo**: `StepOutcome` por passo (estado, duração,
  erro); na primeira falha os restantes ficam `SKIPPED` — o relatório cobre
  o plano integral.
- **Agendar deterministicamente**: `Scheduler.run` ordena por prioridade
  (`CRITICAL > HIGH > NORMAL > LOW`, ordenação estável) e recolhe um
  relatório agregado (contagens, ordem efectiva, duração).

## Ficheiros criados/alterados

- `src/wsai2/runtime_engine/base.py` — contratos: `StepRunner`,
  `StepStatus`, `ExecutionStatus`, `StepOutcome`, `ExecutionReport`,
  `ScheduleOutcome`, `SchedulerReport` (tipos e estados, sem lógica)
- `src/wsai2/runtime_engine/manager.py` — `RuntimeManager.execute_plan`
  (validação, contexto por omissão, políticas, relatório)
- `src/wsai2/runtime_engine/scheduler.py` — `Scheduler.run` (ordenação,
  `stop_on_failure`, contexto por plan, relatório agregado)
- `src/wsai2/runtime_engine/__init__.py` — exports públicos do submódulo
- `tests/test_runtime_engine.py` — 22 testes
- `docs/runtime_engine/BASE-29-runtime-engine.md` — este relatório

Nenhum módulo existente das Fases 1–7 nem das unidades 8.1–8.4 foi
alterado.

## Dependências

- `base.py`: `wsai2.core.context` (`ExecutionPriority`) e
  `wsai2.core.errors` (`WsaiError`); `wsai2.task` apenas em
  `TYPE_CHECKING` (tipagem de `StepRunner`/planos).
- `manager.py`: `wsai2.execution.execute_with_policies` (8.4),
  `wsai2.core` (contexto e erros), `wsai2.task` (`ExecutionPlan`);
  `RecoveryPolicy`/`TimeoutPolicy`/`ResourceGovernor` em `TYPE_CHECKING`
  (injectados por argumento).
- `scheduler.py`: `RuntimeManager` do próprio subsistema e
  `wsai2.core.context`.
- Direcção das dependências: `runtime_engine` aponta para dentro
  (core, execution, resource, task) e é folha do runtime; não cria ciclo.
- **Não duplica**: a execução de passos usa `execute_with_policies` (8.4)
  em vez de reimplementar timeout/retry/reserva; a validade do plano é a
  propriedade `ExecutionPlan.is_executable` já existente.

## Decisões arquitecturais registadas

1. **O plano é a unidade de políticas; o passo é a unidade de
   observação.** `execute_with_policies` aplica timeout/recuperação/
   orçamento a todo o plano (uma única reserva, deadline única e retry do
   plano inteiro); dentro do plano, cada passo é cronometrado e registado
   como `StepOutcome`. Privilegia o relatório exaustivo (passos `SKIPPED`
   incluídos) sem multiplicar reservas/políticas por passo.
2. **Recuperação por plano inteiro:** em `retry`, a tentativa reinicia o
   plano do início e o registo de passos é limpo por tentativa (a lista é
   partilhada mas reiniciada) — o relatório reflecte a última tentativa.
3. **Runner injectado, gestor sem conhecimento de fornecedores:** o passo
   é uma acção opaca `(índice, descrição) -> objecto`; sem runner, a
   execução valida o fluxo e as políticas sem trabalho efectivo ("registar
   sem operação"), nunca chamando o Provider/Model Runtime directamente.
4. **Erros normalizados na taxonomia 8.2:** falhas não taxonómicas de um
   passo são embrulhadas em `ExecutionError` (`wsai.execution.step_failed`
   / `wsai.execution.not_executable`); erros já taxonómicos preservam-se
   intactos. A leitura é feita por `report.status` + `report.error` — a
   execução **devolve relatório mesmo em falha**, sem excepções à frente
   do consumidor do Runtime Engine.
5. **Scheduler simples e determinístico:** ordenação por prioridade com
   ordenação estável (mesma prioridade → ordem original), execução
   sequencial, `stop_on_failure` opcional. Não inventa concorrência que a
   base ainda não garante (a 8.4 executou com thread por plano).
6. **Identidade por omissão:** sem contexto fornecido, o gestor cria
   `ExecutionContext(execution_id=f"exec-{task_id}", task_id=...)`. Um
   contexto com `task_id` diferente do plano é rejeitado
   (`wsai.execution.task_mismatch`) — invariante de coerência tarefa.
7. **Coerência com o foco "hardening 06 vs 07":** a obediência ao
   cancelamento cooperativo entre passos permanece responsabilidade do
   `step_runner` (o token é thread-agnostic, 8.2); o gestor aplica o
   checkpoint no arranque do plano e deixa o enforcement real à 8.4 — não
   duplica checkpoints nem relógios.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **314 testes aprovados** (22 runtime_engine + 28 execution +
21 resource + 22 core + 12 extension + 39 task + 46 provider + 42 model +
33 capability + 27 runtime + 17 hardware + 5 platform + 3 fundação).
Regressão dos 292 anteriores intacta — alteração 100% aditiva.

Os 22 testes validam:

- gestor: rejeição de entrada que não é plano, plano não executável e
  contexto de outra tarefa;
- execução bem-sucedida (ordem dos passos, identidade por omissão,
  contexto fornecido, sem runner, plano sem passos);
- falhas: primeira falha marca o passo e `SKIPPED` nos restantes; erro
  taxonómico preservado; cancelamento antecipado; timeout do plano;
  recuperação (retry do plano inteiro);
- governação: reserva/libertação de recursos observada durante os passos;
  orçamento insatisfeito falha sem executar passos;
- integração com a Fase 7 (plano real `build_execution_plan` executado);
- scheduler: prioridade determinística; estabilidade na mesma prioridade;
  `context_factory`; contagens com falha; continuação após falha;
  interrupção com `stop_on_failure`; tipos e metadados do relatório.

## Estado da fase

Fase 8 — Runtime Engine: concluídas **8.1** (Extension Contract),
**8.2** (Execution Context + Error Model), **8.3** (Resource Governance) e
**8.4** (Execution Policies). A presente unidade **8.5** conclui o gestor
de execução e o scheduler básico.

## Próximo passo

**Fase 8.6 — Lifecycle + Compatibility** (hardening 02 e 08): verificar
`wsai2.extension.lifecycle` existente, integrar o estado de execução das
extensões com `RuntimeStatus` guardado no registo, e adicionar
versioning/compatibilidade de contratos antes da execução. Concorrência
entre planos e filas multicamadas devem ser avaliadas depois da 8.6,
junto com a monitorização contínua (todas anunciadas como posteriores à
8.5).