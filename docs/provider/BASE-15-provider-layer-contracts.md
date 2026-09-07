# WORKSTATION AI 2 — RELATÓRIO DA BASE: PROVIDER LAYER (CONTRATOS E REGISTO)

## O que foi feito

Foi iniciada a **Fase 6 — Provider Layer** com os **contratos de
fornecedor** e o **registo central**: o contrato declarativo
`ProviderDefinition` (id, nome, tipo, endpoint base e capacidades
disponibilizadas) e `ProviderRegistry` com um catálogo base declarativo.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.6 Provider Layer** descrito em
`docs/architecture/ARCHITECTURE.md` ("Isola os fornecedores e motores
concretos, como runtimes locais e APIs compatíveis") e ao item
*contratos de fornecedor* do roadmap da Fase 6. Segue o padrão das fases
anteriores (Capability Engine, Model Intelligence): domínio puro, dados
declarativos, contrato em `base.py` e registo em `registry.py`.

## Para que serve

- Descreve, de forma declarativa, os fornecedores que o WorkStation AI 2
  conhece — runtimes locais (Ollama, llama.cpp) e APIs remotas
  compatíveis (tipo OpenAI), com endpoint base predefinido.
- Liga os fornecedores ao Capacity Engine: `capabilities_provided`
  declara as capacidades do sistema que o fornecedor pode disponibilizar.
- Mantém e consulta o catálogo de fornecedores (`ProviderRegistry`),
  base para a detecção, os adaptadores e os health checks das unidades
  seguintes.

## Ficheiros criados/alterados

- `src/wsai2/provider/base.py` — `ProviderType`, `ProviderDefinition`
- `src/wsai2/provider/registry.py` — `ProviderRegistry`,
  `default_providers`, `create_default_registry`
- `src/wsai2/provider/__init__.py` — exports públicos
- `tests/test_provider.py`
- `docs/provider/BASE-15-provider-layer-contracts.md`

## Dependências

- Domínio puro: sem dependências de plataforma ou de terceiros.
- Referência indirecta ao Capability Engine: `capabilities_provided`
  usa os ids do catálogo de capacidades (ex.: `local_llm_inference`).
- Entradas do catálogo são dados, sem lógica.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **135 testes aprovados** (11 provider + 42 model + 33
capability + 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- catálogo base com 3 fornecedores (2 locais + 1 remoto);
- tipos e campos coerentes (tipo, URI, capacidades);
- registo: obter/verificar, registar com substituição, remover, vazio;
- resumo textual do fornecedor.

## Estado da fase

**Fase 6 — Provider Layer** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contratos de fornecedor ✓
- registo de fornecedores ✓ (catálogo)

Itens pendentes:

- detecção;
- adaptadores de runtime;
- health checks.

## Próximo passo

Unidade seguinte da Fase 6: **detecção de fornecedores** — detectar no
ambiente real quais fornecedores do registo estão presentes e
acessíveis (ex.: contacto com o endpoint base), separando a
disponibilidade declarada do estado detectado.