# WORKSTATION AI 2 — RELATÓRIO DA BASE: MODEL INTELLIGENCE (REGISTO E METADADOS)

## O que foi feito

Foi iniciada a **Fase 5 — Model Intelligence** com o **registo de
modelos, metadados e requisitos**: o contrato declarativo de um modelo
conhecido pelo sistema (`ModelDefinition` com `ModelMetadata` e
`ModelRequirements`) e o registo central `ModelRegistry` com um catálogo
base declarativo.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.5 Model Intelligence** descrito em
`docs/architecture/ARCHITECTURE.md` ("Mantém informação sobre modelos,
requisitos, compatibilidade, desempenho e adequação às tarefas") e aos
três primeiros itens do roadmap da Fase 5: *registo de modelos*,
*metadados* e *requisitos*. Segue o mesmo padrão da Fase 4 (Capability
Engine): domínio puro, dados declarativos, contrato em `base.py` e
registo em `registry.py`.

## Para que serve

- Descreve, de forma declarativa, os modelos que o WorkStation AI 2
  conhece — id, nome, tipo (LLM / embedding), metadados (versão,
  parâmetros, janela de contexto, licença, arquitectura).
- Quantifica os requisitos mínimos por modelo (`ModelRequirements`),
  incluindo as **capacidades do sistema requeridas** (ligação ao
  Catálogo do Capability Engine via ids).
- Mantém e consulta o catálogo de modelos (`ModelRegistry`), base para a
  compatibilidade e a recomendação das unidades seguintes da Fase 5.

## Ficheiros criados/alterados

- `src/wsai2/model/base.py` — `ModelKind`, `ModelMetadata`,
  `ModelRequirements`, `ModelDefinition`
- `src/wsai2/model/registry.py` — `ModelRegistry`, `default_models`,
  `create_default_registry`
- `src/wsai2/model/__init__.py` — exports públicos
- `tests/test_model.py`
- `docs/model/BASE-11-model-intelligence-metadata.md`

## Dependências

- Domínio puro: sem dependências de plataforma ou de terceiros.
- Referência indirecta ao Capability Engine: `ModelRequirements.
  required_capabilities` usa os ids do catálogo de capacidades
  (ex.: `local_llm_inference`, `local_embeddings`).
- Entradas do catálogo são dados, sem lógica.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **93 testes aprovados** (11 model + 33 capability + 3 fundação
+ 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- catálogo base com 3 modelos (2 LLM + 1 embedding);
- tipos e campos coerentes (metadados, requisitos);
- referência correcta às capacidades requeridas e a `has_gpu_requirement`;
- registo: obter/verificar, registar com substituição, remover, vazio;
- resumo textual do modelo.

## Estado da fase

**Fase 5 — Model Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- registo de modelos ✓
- metadados ✓
- requisitos ✓

Itens pendentes:

- compatibilidade;
- classificação;
- recomendação.

## Próximo passo

Unidade seguinte da Fase 5: **compatibilidade dos modelos** — avaliar cada
modelo do registo contra o `HardwareProfile`/`RuntimeProfile` e contra as
capacidades requeridas, seguindo o padrão da avaliação do Capability
Engine.