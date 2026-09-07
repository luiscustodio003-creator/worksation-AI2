# WORKSTATION AI 2 — RELATÓRIO DA BASE: TASK INTELLIGENCE (PLANO DE EXECUÇÃO)

## O que foi feito

Foi implementado o **plano de execução** de uma tarefa: a integração
completa dos requisitos, da viabilidade (Capability Engine), da
recomendação de modelo (Model Intelligence) e de um fornecedor saudável
(Provider Layer) num plano determinístico com passos. É a unidade que
**encerra a Fase 7 — Task Intelligence**.

## Onde se encaixa na arquitectura

Item *plano de execução* do roadmap da **Fase 7** (subsistema 3.7).
Cumpre o fluxo de decisão da arquitectura:

```text
Tarefa → requisitos → capacidades → modelo recomendado → fornecedor saudável → plano
```

Respeita o artigo 13: a selecção de modelo (recomendação) e a selecção
de fornecedor (health checks injectados) permanecem decisões separadas.

## Para que serve

- Produz a decisão "o que fazer para executar esta tarefa" já com o
  **modelo** e o **fornecedor** concretos, pronta a consumir pelo
  Runtime Engine (fase seguinte).
- Não executou I/O: os health checks são injectados como `ProviderHealth`.
- Justifica planos não executáveis (capacidades em falta, sem modelo,
  sem fornecedor saudável).

## Ficheiros criados/alterados

- `src/wsai2/task/plan.py` — `ExecutionPlan`, `build_execution_plan`
- `src/wsai2/task/__init__.py` — novos exports
- `tests/test_task_plan.py`
- `docs/task/BASE-24-task-intelligence-execution-plan.md`

## Dependências

- `plan.py`: contrato, requisitos, selecção de capacidades (locais);
  `wsai2.model` (recomendação), `wsai2.provider` (health),
  `wsai2.capability/hardware/runtime` (entradas).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **209 testes aprovados** (8 plano + 7 selecção + 8 requisitos
+ 7 classificação + 9 task + 46 provider + 42 model + 33 capability + 3
fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- plano executável de chat e de embedding (modelo + fornecedor certos);
- inviabilidade por capacidades em falta; sem fornecedor saudável;
- fornecedor sem as capacidades do modelo ignorado;
- escolha determinística entre fornecedores saudáveis;
- fornecedor degradado excluído;
- limite de recursos sem modelo compatível.

## Estado da fase

**Fase 7 — Task Intelligence — CONCLUÍDA (100%)**.

Itens do roadmap implementados:

- contrato de tarefa ✓
- classificação de tarefas ✓
- requisitos de tarefa ✓
- selecção de capacidades ✓
- plano de execução ✓

## Próximo passo

Iniciar a **Fase 8 — Runtime Engine** (subsistema 3.8): execução de
tarefas no fornecedor/modelo escolhidos, monitorização, cancelamento e
gestão de recursos. Novo subsistema com decisão estrutural própria — a
iniciar em execução seguinte.