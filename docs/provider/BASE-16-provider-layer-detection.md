# WORKSTATION AI 2 — RELATÓRIO DA BASE: PROVIDER LAYER (DETECÇÃO)

## O que foi feito

Foi implementada a **detecção de fornecedores** no ambiente real: dado
um fornecedor do registo, o sistema verifica se está presente e
acessível no endpoint base, obtendo o resultado da detecção (estado,
latência e erro) de forma determinística.

## Onde se encaixa na arquitectura

Item *detecção* do roadmap da **Fase 6 — Provider Layer** (subsistema
3.6). Assenta directamente nos contratos e no registo da unidade
anterior. Segue a constituição: a lógica de domínio (`detection.py`) é
**pura** e o I/O de rede está isolado em `probes.py`, injectável através
da assinatura `ProviderProbe` (artigo 5 da constituição).

## Para que serve

- Distingue a **disponibilidade declarada** (o fornecedor existe no
  catálogo) da **disponibilidade real** (o endpoint responde).
- Prepara o terreno para os health checks: a detecção só confirma
  presença/acessibilidade; a saúde fina é responsabilidade da unidade
  seguinte.
- A separação domínio/I-O permite testar toda a lógica de decisão sem
  rede e trocar a estratégia de contacto (ex.: proxy, autenticação,
  outra versão de protocolo) sem tocar no núcleo.

## Ficheiros criados/alterados

- `src/wsai2/provider/detection.py` — `ProviderProbeResult`, `ProviderProbe`,
  `ProviderDetection`, `detect_provider`, `detect_providers`,
  `available_providers`
- `src/wsai2/provider/probes.py` — `health_probe` (HTTP, isolado)
- `src/wsai2/provider/__init__.py` — novos exports
- `tests/test_provider_detection.py`
- `docs/provider/BASE-16-provider-layer-detection.md`

## Dependências

- `detection.py`: domínio puro; depende de `provider.base` e `provider.registry`.
- `probes.py`: I/O de rede (`urllib.request`) isolado; a detecção usa-o
  apenas via `ProviderProbe`. Sem dependências de terceiros.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **146 testes aprovados** (11 detecção + 11 provider + 42
model + 33 capability + 3 fundação + 5 platform + 17 hardware + 24
runtime).

Os testes validam:

- sucesso/falha de probe com propagação de latência e erro;
- uso da base_url predefinida e override por fornecedor;
- propagação das capacidades declaradas e resumo textual;
- ordem determinística da detecção do registo (por id);
- filtragem de fornecedores acessíveis;
- probe HTTP real contra um servidor local (sucesso) e contra porta
  fechada (falha), sem dependência de serviços externos.

## Estado da fase

**Fase 6 — Provider Layer** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contratos de fornecedor ✓
- registo de fornecedores ✓
- detecção ✓

Itens pendentes:

- adaptadores de runtime;
- health checks.

## Próximo passo

Unidade seguinte da Fase 6: **adaptadores de runtime** — abstração de
comunicação com os runtimes concretos (ex.: listar modelos, executar
inferência) atrás de uma interface estável por tipo de fornecedor,
continuando a manter a interface de I/O separada do domínio.