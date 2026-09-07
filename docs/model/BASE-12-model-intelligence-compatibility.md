# WORKSTATION AI 2 — RELATÓRIO DA BASE: MODEL INTELLIGENCE (COMPATIBILIDADE)

## O que foi feito

Foi implementada a **compatibilidade dos modelos** na Fase 5 — Model
Intelligence: dado o `HardwareProfile` (capacidade estrutural), o
`RuntimeProfile` (estado momentâneo) e o registo de capacidades do
Capability Engine, o sistema determina se cada modelo conhecido está
**disponível**, **condicionado** ou **indisponível** neste instante, com
verificações explícitas por requisito e pelas capacidades requeridas.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.5 Model Intelligence** descrito em
`docs/architecture/ARCHITECTURE.md`, item **compatibilidade** do
roadmap da Fase 5. Espelha a avaliação do Capability Engine (3.4) e
respeita a separação entre *Hardware Capability* e *Runtime State*
(Artigo 5 da Constituição). Também liga os dois subsistemas: a
compatibilidade de um modelo depende das capacidades reais que o
sistema consegue disponibilizar.

## Para que serve

- Avalia `ModelDefinition` (`evaluate_model`) contra o hardware, o
  runtime e as capacidades requeridas.
- Produz `ModelVerdict` com estado (`ModelState`), verificações por
  requisito (`ModelCheck`) e capacidades em falta
  (`missing_capabilities`).
- Disponibiliza `evaluate_models` (todo o registo) e
  `compatible_models` (apenas os compatíveis) — habilita a classificação
  e a recomendação das unidades seguintes.

## Tripla dimensão da compatibilidade

1. **Capacidades do sistema** — `required_capabilities` devem existir e
   estar estruturalmente suportadas no Capability Engine. Capacidade
   indisponível/inexistente → modelo **indisponível**; capacidade apenas
   condicionada → modelo **condicionado**.
2. **Requisitos estruturais** (RAM total, cores, GPU) — falha → modelo
   **indisponível**.
3. **Requisitos de runtime** (RAM disponível, disco) — falha → modelo
   **condicionado**.

## Ficheiros criados/alterados

- `src/wsai2/model/base.py` — adicionados `ModelState`, `ModelCheck`,
  `ModelVerdict`
- `src/wsai2/model/compatibility.py` — **novo**: `evaluate_model`,
  `evaluate_models`, `compatible_models`
- `src/wsai2/model/__init__.py` — exporta novos tipos e funções
- `tests/test_model_compatibility.py` — **novo**
- `docs/model/BASE-12-model-intelligence-compatibility.md`

## Dependências

- `wsai2.capability` — `CapabilityRegistry`, `CapabilityState`,
  `evaluate_capability` (compatibilidade por capacidades)
- `wsai2.hardware` (`HardwareProfile`)
- `wsai2.runtime` (`RuntimeProfile`)
- Sem dependências novas de terceiros.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **105 testes aprovados** (12 model compatibilidade + 11 model
+ 33 capability + 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- modelo disponível, condicionado por capacidade e indisponível por
  capacidade em falta/inexistente;
- modelo indisponível por estrutura (GPU) e disponível com GPU;
- cobertura de todo o registo, filtragem em `compatible_models`;
- verificações por requisito (capabilities, ram_total, ram_available,
  cpu_cores, gpu, disk) e reflexo de faltas no veredicto.

## Estado da fase

**Fase 5 — Model Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- registo de modelos ✓
- metadados ✓
- requisitos ✓
- compatibilidade ✓

Itens pendentes:

- classificação;
- recomendação.

## Próximo passo

Unidade seguinte da Fase 5: **classificação dos modelos** — agrupar os
modelos por categoria (ex.: família/tipo) e gerar o score de adequação
para recomendações.