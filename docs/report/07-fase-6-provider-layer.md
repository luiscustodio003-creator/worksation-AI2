# WORKSTATION AI 2 — RELATÓRIO DA FASE 6

## PROVIDER LAYER

**Subsistema:** `wsai2.provider`
**Referência arquitectural:** subsistema 3.6
**Roadmap:** Fase 6
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

O WSAI 2 não reinventa motores de inferência. O problema que a Fase 6 resolve é **isolar os fornecedores e motores concretos** (runtimes locais e APIs compatíveis) atrás de contratos estáveis:

> "O que quero executar?" é o modelo (Fase 5). "Como e onde posso executar?" é o fornecedor (esta fase).

O mesmo modelo pode ser executado por diferentes runtimes. Separar os conceitos permite ao WSAI 2 evoluir sem ficar preso a uma tecnologia específica — hoje Ollama, llama.cpp ou APIs compatíveis com OpenAI; amanhã outros motores, sem reconstruir o Core.

## 2. ARQUITECTURA DA FASE

```text
wsai2.provider
  ├── base.py        → ProviderDefinition, ProviderType (local_runtime / remote_api)
  ├── registry.py    → registo central + catálogo base
  ├── detection.py   → domínio puro da detecção
  ├── probes.py      → I/O de rede isolado (probes injectáveis)
  ├── adapters.py    → RuntimeAdapter por tipo de fornecedor
  ├── transports.py  → transporte HTTP injectável
  └── health.py      → health checks finos (saudável / degradado / indisponível)
```

### O percurso de decisão

```text
Contratos e registo (que fornecedores existem)
  → Detecção (quais estão presentes e acessíveis)
  → Adaptadores (como comunicar com cada um)
  → Health checks (qual está saudável agora)
```

### O catálogo base

- **Ollama** (protocolo nativo);
- **llama.cpp** (através do protocolo compatível com OpenAI);
- **adaptador genérico** para APIs compatíveis com OpenAI.

Toda a comunicação externa é feita através de **adaptadores e transportes injectáveis** — a lógica de decisão permanece pura e testável sem rede.

## 3. ARTIGO 13 — INDEPENDÊNCIA DE FORNECEDORES

Esta fase é o cumprimento prático do artigo 13 da Constituição:

> O WSAI 2 não pode depender de um modelo, fabricante, repositório, runtime de inferência ou fornecedor específico. Um novo fornecedor deve poder ser integrado através do contrato e dos adaptadores apropriados **sem alterar a lógica central do domínio**.

Um fornecedor concreto é **substituível** por outro que implemente o mesmo contrato.

## 4. CONEXÃO COM A VISÃO

>A visão declara que não estamos a tentar fazer um "novo Ollama": "Ollama pode ser um provider. llama.cpp pode ser um backend. vLLM pode ser um backend/provider adequado a determinadas máquinas e cenários. Outros runtimes podem ser adicionados."

A Fase 6 transforma essa decisão em arquitectura: o WSAI 2 decide; o provider executa. Beneficiamos do trabalho dos motores especializados sem depender deles estruturalmente.

## 5. EVIDÊNCIA E VALIDAÇÃO

- Testes: `tests/test_provider*.py` (46 testes na fase — contratos, detecção, adaptadores, health).
- Detecção com domínio puro (`detection.py`) e I/O isolado em `probes.py` (artigo 5 da Constituição).
- Adaptadores testáveis sem rede (transporte injectável); erros normalizados em `AdapterError`.
- Health checks finos validados contra servidor local controlado; fornecedores sem adaptador reportados como `DEGRADED` (não propagam erros).

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: integrar vários motores (Ollama, llama.cpp, APIs compatíveis) sem prender o sistema a um deles.
2. Solução: Provider Layer com contratos, registo, detecção, adaptadores e health checks.
3. O WSAI 2 não é um "novo Ollama" — os motores existentes são os fornecedores.
4. Ideia central: **modelo ≠ fornecedor** (artigo 13). A pluralidade de motores é uma característica, não uma dependência.
5. Papel no pipeline: *que provider pode executar este modelo e está saudável agora?*