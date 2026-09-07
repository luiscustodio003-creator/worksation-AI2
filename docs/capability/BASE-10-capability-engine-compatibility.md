# WORKSTATION AI 2 — RELATÓRIO DA BASE: CAPABILITY ENGINE (COMPATIBILIDADE)

## O que foi feito

Foi implementado o **relatório de compatibilidade** do Capability Engine:
a consolidação final da Fase 4. Para cada capacidade conhecida do
registo, o relatório associa a definição estrutural ao veredicto da
avaliação (disponível / condicionada / indisponível) e apresenta uma
**justificação textual** que explica o estado em linguagem natural,
referindo os requisitos não satisfeitos e os valores exigidos e
disponíveis.

## Onde se encaixa na arquitectura

Completa o subsistema **3.4 Capability Engine** (Fase 4 do roadmap):
os itens *definições*, *registo*, *avaliação*, *compatibilidade* e
*capacidades disponíveis* ficam todos implementados. A compatibilidade
recorda a separação entre *Hardware Capability* e *Runtime State*
(Artigo 5): a justificação distingue explicitamente falhas estruturais
(indisponível) de recursos momentâneos (condicionada).

## Para que serve

- Consolida a avaliação num relatório por capacidade
  (`build_compatibility` → `CompatibilityReport`).
- Expõe o catálogo final de capacidades disponíveis
  (`report.available`).
- Presta uma justificação em linguagem natural por capacidade
  (`CapabilityCompatibility.justification`), pronta para exposição na
  API e na UI.
- Preserva o hardware e o runtime que originaram o relatório.

## Ficheiros criados/alterados

- `src/wsai2/capability/base.py` — adicionados `CapabilityCompatibility`
  e `CompatibilityReport` (com agrupamentos por estado e resumo)
- `src/wsai2/capability/compatibility.py` — **novo**: `build_compatibility`
- `src/wsai2/capability/__init__.py` — exporta novos tipos e função
- `tests/test_capability_compatibility.py` — **novo**
- `docs/capability/BASE-10-capability-engine-compatibility.md`

## Dependências

- `wsai2.capability.registry` (definições)
- `wsai2.capability.evaluation` (veredictos)
- `wsai2.hardware` e `wsai2.runtime` (entradas)
- Sem dependências novas de terceiros.

Nota de design: o módulo de compatibilidade apenas **consolida**
informação produzida pelo Capability Engine — não repete lógica de
avaliação nem de decisão de estado.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **82 testes aprovados** (11 capability + 10 avaliação + 12
compatibilidade + 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- uma entrada por capacidade registada;
- estados esperados no cenário de teste (2 disponíveis, 1 condicionada,
  1 indisponível);
- agrupamentos por estado coerentes com `is_available`;
- coerência com `available_capabilities`; distinção de capacidades com
  e sem GPU suficiente;
- justificações: disponível, condicionada por runtime (RAM disponível)
  e indisponível por estrutura (GPU/VRAM), com valores referidos;
- resumo com contagens correctas e preservação de hardware/runtime.

## Estado da fase

**Fase 4 — Capability Engine — CONCLUÍDA (100%)**.

Itens do roadmap implementados:

- definições de capacidade ✓
- registo ✓
- avaliação ✓
- compatibilidade ✓
- capacidades disponíveis ✓

## Próximo passo

Iniciar a **Fase 5 — Model Intelligence** (subsistema 3.5 da
arquitectura): registo de modelos, metadados, requisitos e
compatibilidade. Não será iniciada na mesma execução por abrir um novo
subsistema com decisão estrutural própria.