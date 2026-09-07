# WORKSTATION AI 2 — RELATÓRIO DA BASE: PROVIDER LAYER (HEALTH CHECKS)

## O que foi feito

Foram implementados os **health checks** dos fornecedores: a avaliação
da saúde fina de cada fornecedor — endpoint acessível **e** motor a
responder correctamente — combinando a detecção com os adaptadores, com
classificação em estados (saudável / degradado / indisponível). Esta é a
unidade que **encerra a Fase 6 — Provider Layer**.

## Onde se encaixa na arquitectura

Item *health checks* do roadmap da **Fase 6** (subsistema 3.6). Cada
unidade da fase alimentou a seguinte e esta é o fecho:

contratos → registo → detecção → adaptadores → **health checks**.

Mantém o padrão das unidades anteriores: o módulo de decisão
(`health.py`) é puro e todo o I/O (probe + transporte) é injectado.

## Para que serve

- Dá uma **decisão única** sobre a saúde de um fornecedor: inacessível,
  acessível mas com motor com problemas, ou operacional (com o número
  de modelos expostos).
- Consome a presença (detecção) e a capacidade de listar modelos
  (adaptador) sem duplicar lógica.
- Fornece, para a Task Intelligence (Fase 7), a informação de quais
  fornecedores estão realmente prontos a usar.

## Ficheiros criados/alterados

- `src/wsai2/provider/health.py` — `ProviderHealthStatus`,
  `ProviderHealth`, `check_provider_health`, `check_providers_health`,
  `healthy_providers`
- `src/wsai2/provider/__init__.py` — novos exports
- `tests/test_provider_health.py`
- `docs/provider/BASE-18-provider-layer-health.md`

## Dependências

- `health.py`: usa a detecção (`ProviderProbeResult`), os adaptadores
  (`RuntimeAdapter`, `AdapterError`, `build_adapter`) e os contratos.
- I/O completamente injectado; a iteração real (probe HTTP +
  transporte HTTP) entra apenas via argumentos.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **170 testes aprovados** (10 health + 14 adapters + 11
detecção + 11 provider + 42 model + 33 capability + 3 fundação + 5
platform + 17 hardware + 24 runtime).

Os testes validam:

- endpoint inacessível → UNAVAILABLE (sem contactar o motor);
- motor com falha → DEGRADED; operacional → HEALTHY com contagem;
- base_url personalizada e resumo;
- fornecedores sem adaptador registado → DEGRADED reportado (não
  propagam o erro);
- health check do registo completo, ordenado por id;
- filtragem de saudáveis;
- integração real probe HTTP + adaptador + transporte contra servidor
  local.

## Estado da fase

**Fase 6 — Provider Layer — CONCLUÍDA (100%)**.

Itens do roadmap implementados:

- contratos de fornecedor ✓
- registo de fornecedores ✓
- detecção ✓
- adaptadores de runtime ✓
- health checks ✓

## Próximo passo

Iniciar a **Fase 7 — Task Intelligence** (subsistema 3.7): tarefas e
planos, selecção de fornecedor/modelo por tarefa, execução e gestão de
erros. Novo subsistema com decisão estrutural própria — a iniciar em
execução seguinte.