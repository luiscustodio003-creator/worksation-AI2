# WORKSTATION AI 2 — RELATÓRIO DA BASE: CAPABILITY ENGINE (AVALIAÇÃO)

## O que foi feito

Foi implementada a **avaliação de capacidades** na Fase 4 — Capability
Engine: dado o `HardwareProfile` (capacidade estrutural) e o
`RuntimeProfile` (estado momentâneo), o sistema determina se cada
capacidade está **disponível**, **condicionada** ou **indisponível**
neste instante, com verificações explícitas por requisito.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.4 Capability Engine** descrito em
`docs/architecture/ARCHITECTURE.md`, item **avaliação** do roadmap.
Respeita a separação fundamental entre *Hardware Capability* e
*Runtime State* (Artigo 5 da Constituição): um requisito estrutural
falhado torna a capacidade *indisponível*; um requisito de runtime
falhado torna-a *condicionada* (suportada, mas não executável já).

## Para que serve

- Avalia `CapabilityDefinition` (via `evaluate_capability`) contra o
  hardware e o runtime reais.
- Produz `CapabilityVerdict` com estado (`CapabilityState`) e
  verificações por requisito (`RequirementCheck`) que justificam o
  resultado.
- Disponibiliza `evaluate_capabilities` (todo o registo) e
  `available_capabilities` (apenas as disponíveis) — base para o item
  "capacidades disponíveis" do roadmap.

## Ficheiros criados/alterados

- `src/wsai2/capability/base.py` — adicionados `CapabilityState`,
  `RequirementCheck`, `CapabilityVerdict`
- `src/wsai2/capability/evaluation.py` — **novo**: verificação e derivação
  de estado; `evaluate_capability`, `evaluate_capabilities`,
  `available_capabilities`
- `src/wsai2/capability/__init__.py` — exporta novos tipos e funções
- `tests/test_capability_evaluation.py` — **novo**
- `tests/test_runtime.py` — corrigida asserção de `cpu_percent` de
  processos (em Windows pode ultrapassar 100% com vários cores)
- `docs/capability/BASE-09-capability-engine-evaluation.md`

## Dependências

- `wsai2.hardware` (`HardwareProfile`)
- `wsai2.runtime` (`RuntimeProfile`)
- Sem dependências novas de terceiros.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **70 testes aprovados** (11 capability + 10 capability avaliação
+ 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- Capacidade totalmente satisfeita → AVAILABLE;
- Falha estrutural (GPU exigida/VRAM insuficiente, RAM total) →
  UNAVAILABLE;
- Falha de runtime (RAM disponível insuficiente) → RESTRICTED;
- Checks por requisito (ram_total, ram_available, cpu_cores, gpu, disk)
  correctos e justificáveis;
- Avaliação de todo o registo e filtragem de disponíveis.

## Estado da fase

**Fase 4 — Capability Engine** — **EM PROGRESSO**.

Itens do roadmap implementados:

- definições de capacidade ✓
- registo ✓
- avaliação ✓
- capacidades disponíveis ✓ (via `available_capabilities`)

Itens pendentes:

- compatibilidade (relatório de compatibilidade consolidado por
  capacidade).

## Próximo passo

Unidade seguinte da Fase 4: **compatibilidade** — relatório consolidado
que apresenta, para cada capacidade do registo, o estado, os requisitos
e uma justificação textual, fechando o Catálogo de capacidades
disponíveis. Reflecte o planeamento já registado em `PROJECT_STATE.md`.