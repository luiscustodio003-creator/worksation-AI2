# WORKSTATION AI 2 — RELATÓRIO DA BASE: MODEL INTELLIGENCE (CLASSIFICAÇÃO)

## O que foi feito

Foi implementada a **classificação dos modelos** na Fase 5 — Model
Intelligence: cada modelo conhecido recebe uma **categoria funcional
primária** (chat / completion / embedding) e um **score de adequação**
(0.0–1.0) derivado de forma determinística do veredicto de
compatibilidade.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.5 Model Intelligence**, itens
**classificação** do roadmap da Fase 5. Assenta directamente na
compatibilidade (unidade anterior) e prepara a **recomendação** (última
unidade da fase), que combinará categoria, score e critérios da tarefa.

## Para que serve

- Atribui **categoria funcional** a cada modelo: declarada na definição
  ou derivada do tipo (LLM → chat; embedding → embedding).
- Produz um **score de adequação** comparável entre modelos, pronto para
  ordenação/recomendação.
- Disponibiliza `classify_model` (um modelo) e `classify_models` (todo o
  registo), devolvendo `ModelClassification` (categoria + score +
  veredicto que o justifica).

## Rubrica do score de adequação

| Estado do modelo | Score | Significado |
|---|---|---|
| AVAILABLE | 1.0 | Requisitos do modelo e capacidades requeridas satisfeitos |
| RESTRICTED | 0.5 | Executável, mas condicionado por capacidades/runtime |
| UNAVAILABLE | 0.0 | Requisitos mínimos ou capacidades requeridas não satisfeitos |

Rubrica determinística e documentada — a base simples que a unidade de
recomendação irá combinar com os critérios da tarefa.

## Ficheiros criados/alterados

- `src/wsai2/model/base.py` — adicionado `ModelCategory`; campo
  `category` em `ModelDefinition`
- `src/wsai2/model/registry.py` — catálogo base com categorias
- `src/wsai2/model/classification.py` — **novo**: `ModelClassification`,
  `category_for`, `adequacy_score`, `classify_model`, `classify_models`
- `src/wsai2/model/__init__.py` — exporta novos tipos e funções
- `tests/test_model_classification.py` — **novo**
- `docs/model/BASE-13-model-intelligence-classification.md`

## Dependências

- `wsai2.model.compatibility` (veredictos; `evaluate_models`)
- `wsai2.capability`, `wsai2.hardware`, `wsai2.runtime` (entradas)
- Sem dependências novas de terceiros.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **114 testes aprovados** (9 classificação + 23 model + 33
capability + 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- categorias declaradas no catálogo e derivadas do tipo,
  com sobreposição pela declaração;
- rubrica do score (1.0 / 0.5 / 0.0) por estado;
- classificação individual e de todo o registo;
- coerência entre score, `is_available` e estado do veredicto.

## Estado da fase

**Fase 5 — Model Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- registo de modelos ✓
- metadados ✓
- requisitos ✓
- compatibilidade ✓
- classificação ✓

Item pendente:

- recomendação.

## Próximo passo

Unidade que encerra a **Fase 5**: **recomendação de modelos** — escolher
o modelo mais adequado para um dado conjunto de critérios (categoria,
compatibilidade, score), devolvendo a recomendação com justificação e
alternativas.