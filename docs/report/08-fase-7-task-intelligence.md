# WORKSTATION AI 2 — RELATÓRIO DA FASE 7

## TASK INTELLIGENCE

**Subsistema:** `wsai2.task`
**Referência arquitectural:** subsistema 3.7
**Roadmap:** Fase 7
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

Até aqui, o sistema conhece a máquina (Fase 2), o estado actual (Fase 3), as capacidades utilizáveis (Fase 4), os modelos (Fase 5) e os fornecedores (Fase 6). Mas falta o que **une tudo**: a tarefa que o utilizador pediu.

A Fase 7 resolve esse problema — **interpretar a tarefa, identificar os seus requisitos e produzir o plano de execução**:

> "Tenho esta tarefa. Analisa o que tenho disponível e determina a melhor forma de a executar."

A tarefa passa a ser o ponto de partida de toda a cadeia de inteligência. É aqui que o sistema deixa de pensar "tenho um modelo" e passa a pensar "tenho uma tarefa, uma máquina, um conjunto de recursos e várias possibilidades de execução".

## 2. ARQUITECTURA DA FASE

```text
wsai2.task
  ├── base.py                  → Task, TaskKind (chat / completion / embedding)
  ├── classification.py        → classificação da tarefa por categoria de modelo
  ├── requirements.py          → TaskRequirements (categoria + capacidades exigidas)
  ├── capability_selection.py  → verificação de viabilidade contra o Capability Engine
  └── plan.py                  → build_execution_plan: o plano final
```

### O percurso de decisão

```text
Tarefa (o que o utilizador pediu)
  → Classificação (que tipo/categoria de modelo)
  → Requisitos (de que capacidades precisa)
  → Selecção de capacidades (está a máquina apta? viável?)
  → Plano de execução (ExecutionPlan fechado)
```

### O ExecutionPlan

O `ExecutionPlan` consolida:

- **feasible** — se a execução é viável;
- **model_id** — modelo recomendado;
- **provider_id** — fornecedor saudável e compatível;
- **reasons** — justificações de viabilidade ou inviabilidade;
- **steps** — passos de execução;
- **`is_executable`** — se pode ser submetido ao Runtime Engine.

O health check dos fornecedores é **injectado** (`ProviderHealth`) — o plano não faz I/O.

## 3. INTEGRAÇÃO COM AS OUTRAS FASES

O Task Intelligence é o grande **consumidor-orquestrador** das fases anteriores:

```text
Capability Engine (Fase 4)  → selecção e viabilidade de capacidades
Model Intelligence (Fase 5) → categoria e modelo adequado
Provider Layer (Fase 6)     → fornecedor saudável e compatível
Task Intelligence (Fase 7)  → reúne tudo no ExecutionPlan
Runtime Engine (Fase 8)     → executa o ExecutionPlan
```

A selecção de modelo e de fornecedor permanece separada (artigo 13) — o Task Intelligence apenas as **consome** de forma determinística.

## 4. CONEXÃO COM A VISÃO

>A visão descreve a diferença fundamental: "uma aplicação tradicional de IA pergunta 'acho o modelo e executo'. A WSAI 2 pergunta 'o que esta tarefa exige?' e desce pela cadeia de inteligência até ao plano de execução."

A Fase 7 é o **primeiro elo humano da cadeia**: é o momento em que o pedido do utilizador entra no sistema e é traduzido em linguagem de decisão (requisitos, capacidades, modelo, fornecedor, plano).

## 5. EVIDÊNCIA E VALIDAÇÃO

- Testes: `tests/test_task*.py` (39 testes na fase — contrato, classificação, requisitos, selecção, plano).
- `Task` imutável com `TaskKind` e `required_capabilities`; independência total de modelos/fornecedores no contrato.
- `build_execution_plan` fecha o ciclo: requisitos → capacidades → modelo → fornecedor → passos.
- Domínio puro, determinístico, sem I/O.

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: sem entender a tarefa nada é decidido bem — o sistema precisava de um ponto de partida inteligente.
2. Solução: Task Intelligence classifica a tarefa, deriva requisitos, verifica viabilidade e produz o plano.
3. O `ExecutionPlan` reúne: viabilidade, modelo, fornecedor saudável, razões e passos.
4. É o grande consumidor das Fases 2–6 e o abastecedor da Fase 8.
5. Papel no pipeline: *o que esta tarefa exige?* — a pergunta original da visão.