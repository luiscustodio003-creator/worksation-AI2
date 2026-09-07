# WORKSTATION AI 2 — RELATÓRIO DA BASE: RUNTIME INTELLIGENCE (DISPONIBILIDADE EFECTIVA)

## O que foi feito

Completou-se a **Fase 3 — Runtime Intelligence** com a análise derivada
de **disponibilidade efectiva**: a avaliação de até que ponto os recursos
de runtime estão realmente livres para trabalho no momento da amostragem.
O `RuntimeProfile` passa a incluir `RuntimeAvailability` por domínio (CPU,
memória) com scores 0.0–1.0, estados (`HEALTHY`, `DEGRADED`, `CRITICAL`) e
um estado global ponderado (`overall_status`).

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.3 Runtime Intelligence** descrito em
`docs/architecture/ARCHITECTURE.md`. Representa a parte de avaliação do
*Runtime State*: recursos disponíveis e carga, interpretados como
disponibilidade efectiva — distinta de *Hardware Capability* (Artigo 5 da
Constituição). A capacidade estrutural do Hardware Intelligence permanece
intacta.

## Para que serve

- Fornece `RuntimeProfile` completo com `availability` (tupla de
  `RuntimeAvailability`) e `overall_status` (`AvailabilityStatus`).
- Expõe propriedades de conveniência: `cpu_availability`,
  `memory_availability`.
- Permite decisões baseadas em disponibilidade: `is_available`,
  `availability_summary`.
- Quantifica pressão de swap e saturação do CPU como penalizações.

## Ficheiros criados/alterados

- `src/wsai2/runtime/base.py` — adicionados `AvailabilityDomain`,
  `AvailabilityStatus`, `RuntimeAvailability`; `RuntimeProfile` expandido
  com `availability` e `overall_status`
- `src/wsai2/runtime/availability.py` — **novo**: análise e scoring de
  disponibilidade efectiva
- `src/wsai2/runtime/factory.py` — integra `analyze_runtime_availability`
- `src/wsai2/runtime/__init__.py` — exporta novos tipos
- `tests/test_runtime.py` — +10 testes (disponibilidades, estados, domínios,
  análises deterministas)

## Dependências

- `psutil>=5.9` (já presente)
- Runtime Intelligence base (carga do CPU, memória) já implementados

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **49 testes aprovados** (3 fundação + 5 platform + 17 hardware
+ 24 runtime).

Os testes validam:

- Perfil com 2 disponibilidades derivadas (cpu, memory);
- Scores entre 0.0 e 1.0, estados válidos, detalhes por domínio;
- Estado global ponderado (`overall_status`);
- Acessores de conveniência (`cpu_availability`, `memory_availability`);
- Análises deterministas (CPU saturado → crítico; memória livre → saudável);
- Enums `AvailabilityStatus` e `AvailabilityDomain` completos.

## Estado da fase

**Fase 3 — Runtime Intelligence** — **CONCLUÍDA** (100%).

Itens do roadmap Fase 3 implementados:

- recursos disponíveis ✓
- carga ✓
- processos ✓
- estado de execução ✓
- perfil de runtime ✓ (inclui disponibilidade efectiva)

## Próximo passo

Iniciar a **Fase 4 — Capability Engine** (definições de capacidade,
registo, avaliação, compatibilidade, capacidades disponíveis). Esta é a
fase que integra a capacidade estrutural (hardware) e o estado disponível
(runtime) nas capacidades reais que o sistema consegue disponibilizar.