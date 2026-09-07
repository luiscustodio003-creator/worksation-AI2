# WORKSTATION AI 2 — RELATÓRIO DA BASE: TASK INTELLIGENCE (CLASSIFICAÇÃO)

## O que foi feito

Foi implementada a **classificação de tarefas**: o mapeamento
determinístico entre o tipo funcional de uma tarefa e a **categoria de
modelo** mais adequada (`TaskClassification`), ligando o Task
Intelligence ao Model Intelligence.

## Onde se encaixa na arquitectura

Item *classificação de tarefas* do roadmap da **Fase 7 — Task
Intelligence** (subsistema 3.7). Assenta no contrato de tarefa da
unidade anterior e segue o fluxo da arquitectura:

```text
Tarefa → classificação (categoria) → modelo (Model Intelligence) → fornecedor (Provider Layer)
```

Respeita o artigo 13 da constituição: a tarefa decide a **categoria**;
o Model Intelligence decide o **modelo**; o Provider Layer decide o
**fornecedor**.

## Para que serve

- Traduz o pedido do utilizador no domínio de decisão dos modelos
  (chat / completion / embedding).
- Fornece, de forma determinística e testável, o ponto de entrada para
  as unidades seguintes (requisitos, selecção de capacidades e plano).

## Ficheiros criados/alterados

- `src/wsai2/task/classification.py` — `TaskClassification`,
  `category_for_task`, `classify_task`, `classify_tasks`
- `src/wsai2/task/__init__.py` — novos exports
- `tests/test_task_classification.py`
- `docs/task/BASE-21-task-intelligence-classification.md`

## Dependências

- `classification.py`: depende do contrato de tarefa (local) e de
  `wsai2.model.base.ModelCategory` — dependência conceptual apenas da
  categoria (não de fornecedores ou do modelo concreto).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **186 testes aprovados** (7 classificação + 9 task + 46
provider + 42 model + 33 capability + 3 fundação + 5 platform + 17
hardware + 24 runtime).

Os testes validam:

- mapeamento chat/completion/embedding → categoria correspondente;
- conteúdo da classificação (id, tipo, categoria) e resumo;
- o tipo funcional como fonte da verdade (mesmo com capacidades exigidas);
- ordem preservada e conjunto vazio.

## Estado da fase

**Fase 7 — Task Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contrato de tarefa ✓
- classificação de tarefas ✓

Itens pendentes:

- requisitos de tarefa;
- selecção de capacidades;
- plano de execução.

## Próximo passo

Unidade seguinte da Fase 7: **requisitos de tarefa** — materializar as
exigências de uma tarefa (capacidades e categoria de modelo) num
contrato de requisitos consumível pelo Model Intelligence.