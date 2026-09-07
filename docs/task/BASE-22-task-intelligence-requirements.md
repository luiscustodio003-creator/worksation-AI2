# WORKSTATION AI 2 — RELATÓRIO DA BASE: TASK INTELLIGENCE (REQUISITOS)

## O que foi feito

Foram implementados os **requisitos de tarefa**: a materialização das
exigências de uma tarefa num contrato consumível pelo Model
Intelligence (`TaskRequirements`), com a categoria de modelo adequada,
as capacidades exigidas (únicas, por ordem) e o máximo de tokens.

## Onde se encaixa na arquitectura

Item *requisitos de tarefa* do roadmap da **Fase 7 — Task
Intelligence** (subsistema 3.7). Assenta no contrato e na classificação
das unidades anteriores e alimenta a selecção e o plano de execução.

As capacidades vêm **apenas** da tarefa; o subsistema não inventa
capacidades para a tarefa (limite registado na auditoria BASE-19).

## Para que serve

- Entrega ao Model Intelligence exactamente o que a tarefa exige:
  categoria + capacidades + tokens máximos.
- Normaliza as capacidades (deduplica preservando ordem), tornando a
  comparação com o registo de capacidades determinística.

## Ficheiros criados/alterados

- `src/wsai2/task/requirements.py` — `TaskRequirements`,
  `capabilities_for_task`, `requirements_for`, `requirements_for_many`
- `src/wsai2/task/__init__.py` — novos exports
- `tests/test_task_requirements.py`
- `docs/task/BASE-22-task-intelligence-requirements.md`

## Dependências

- `requirements.py`: contrato de tarefa e classificação (locais) +
  `ModelCategory` (conceptual).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **194 testes aprovados** (8 requisitos + 7 classificação + 9
task + 46 provider + 42 model + 33 capability + 3 fundação + 5 platform
+ 17 hardware + 24 runtime).

Os testes validam:

- ordem preservada e deduplicação de capacidades;
- capacidades vazias; conteúdo do contrato (categoria, tokens, resumo);
- categoria derivada do tipo funcional; token por defeito;
- processo em conjunto e vazio.

## Estado da fase

**Fase 7 — Task Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contrato de tarefa ✓
- classificação de tarefas ✓
- requisitos de tarefa ✓

Itens pendentes:

- selecção de capacidades;
- plano de execução.

## Próximo passo

Unidade seguinte da Fase 7: **selecção de capacidades** — verificar
quais das capacidades exigidas estão realmente disponíveis no sistema
(Capability Engine) e validar a viabilidade da tarefa.