# WORKSTATION AI 2 — RELATÓRIO DA BASE: TASK INTELLIGENCE (SELEcÇÃO DE CAPACIDADES)

## O que foi feito

Foi implementada a **selecção de capacidades**: a verificação, contra o
Capability Engine, de quais das capacidades exigidas por uma tarefa
estão realmente disponíveis no sistema, separando as satisfeitas das em
falta e determinando a viabilidade da execução.

## Onde se encaixa na arquitectura

Item *selecção de capacidades* do roadmap da **Fase 7 — Task
Intelligence** (subsistema 3.7). Reutiliza o Capability Engine (Fase 4)
sem duplicar a avaliação — a decisão de "disponível" pertence ao
subsistema de capacidades; o Task Intelligence apenas **selecciona** e
**decide a viabilidade**.

## Para que serve

- Diz, antes de planear, se a tarefa pode ser executada com os recursos
  actuais do sistema.
- Expõe exactamente quais capacidades faltam (ordem de declaração
  preservada) para justificar inviabilidade.
- Delega o estado real (hardware capability vs runtime state) ao
  subsistema correcto.

## Ficheiros criados/alterados

- `src/wsai2/task/capability_selection.py` — `TaskCapabilitySelection`,
  `select_capabilities`
- `src/wsai2/task/__init__.py` — novos exports
- `tests/test_task_capability_selection.py`
- `docs/task/BASE-23-task-intelligence-capability-selection.md`

## Dependências

- `capability_selection.py`: `wsai2.capability` (avaliação),
  `wsai2.hardware` e `wsai2.runtime` (entradas), requisitos (local).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **201 testes aprovados** (7 selecção + 8 requisitos + 7
classificação + 9 task + 46 provider + 42 model + 33 capability + 3
fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- todas as capacidades disponíveis → viável;
- capacidade em falta/inexistente → inviável;
- GPU ausente → `accelerated_ml` em falta; GPU suficiente → disponível;
- sem capacidades exigidas → sempre viável;
- ordem preservada em disponíveis e em falta;
- resumo com contagem.

## Estado da fase

**Fase 7 — Task Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contrato de tarefa ✓
- classificação de tarefas ✓
- requisitos de tarefa ✓
- selecção de capacidades ✓

Itens pendentes:

- plano de execução (encerra a Fase 7).

## Próximo passo

Unidade final da Fase 7: **plano de execução** — integrar requisitos,
viabilidade e recomendação de modelo/fornecedor num plano executável
(qual modelo, que fornecedor saudável, quais passos), encerrando a fase.