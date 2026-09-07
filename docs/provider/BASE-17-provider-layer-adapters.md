# WORKSTATION AI 2 — RELATÓRIO DA BASE: PROVIDER LAYER (ADAPTADORES)

## O que foi feito

Foram implementados os **adaptadores de runtime**: uma interface
estável (`RuntimeAdapter`) para comunicar com os motores concretos —
listar modelos e gerar texto — com implementações para o protocolo
nativo do Ollama e para o protocolo compatível com a API OpenAI
(llama.cpp e APIs remotas), suportadas por um transporte HTTP injectável.

## Onde se encaixa na arquitectura

Item *adaptadores de runtime* do roadmap da **Fase 6 — Provider Layer**
(subsistema 3.6). Assenta nos contratos e no registo das unidades
anteriores. Mantém o padrão da detecção: a lógica de cada adaptador é
pura (usa apenas a assinatura `Transport` injectada) e o I/O de rede
está isolado em `transports.py` (constituição, artigo 5).

## Para que serve

- Permite que a camada acima (Task Intelligence) execute
  listagem/geração sem conhecer o motor concreto: o fornecedor
  `ollama` fala o protocolo nativo; `llama_cpp` e `openai_compatible`
  falam o protocolo compatível com OpenAI.
- A interface é **duplicável**: um futuro wrapper (ex.: chave de API,
  proxy, instrumentação) obtém-se por composição do mesmo contrato.
- Prepara os health checks: a mesma interface servirá para verificar a
  saúde fina de cada motor.

## Ficheiros criados/alterados

- `src/wsai2/provider/adapters.py` — `AdapterError`, `Transport`,
  `TransportResult`, `RuntimeAdapter` (Protocol), `OllamaAdapter`,
  `OpenAiCompatibleAdapter`, `adapter_factory_names`, `build_adapter`
- `src/wsai2/provider/transports.py` — `http_json_transport` (I/O isolado)
- `src/wsai2/provider/__init__.py` — novos exports
- `tests/test_provider_adapters.py`
- `docs/provider/BASE-17-provider-layer-adapters.md`

## Dependências

- `adapters.py`: domínio; depende de `provider.base` e da assinatura
  `Transport` (sem importar transports concretos).
- `transports.py`: I/O de rede (`urllib.request`, JSON) isolado.
- Sem dependências de terceiros.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **160 testes aprovados** (14 adapters + 11 detecção + 11
provider + 42 model + 33 capability + 3 fundação + 5 platform + 17
hardware + 24 runtime).

Os testes validam:

- listagem de modelos e geração de texto para ambos os protocolos,
  incluindo as chamadas feitas (URL, método e payload);
- erros: estado HTTP >= 400, JSON inválido, campos ausentes;
- fábrica de adaptadores por id de fornecedor e erro para desconhecidos;
- transporte HTTP real contra servidor local (sucesso e falha de rede);
- integração adaptador + transporte real.

## Estado da fase

**Fase 6 — Provider Layer** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contratos de fornecedor ✓
- registo de fornecedores ✓
- detecção ✓
- adaptadores de runtime ✓

Itens pendentes:

- health checks (encerra a Fase 6).

## Próximo passo

Unidade final da Fase 6: **health checks** — avaliação da saúde fina de
cada fornecedor (ex.: listar modelos com sucesso/erro, latência,
disponibilidade do motor), reutilizando a detecção e os adaptadores, e
fecho da fase com classificação de estado por fornecedor.