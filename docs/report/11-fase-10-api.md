# WORKSTATION AI 2 — RELATÓRIO DA FASE 10

## API

**Subsistema:** `wsai2.api`
**Referência arquitectural:** subsistema 3.10
**Roadmap:** Fase 10 (API-01 concluída; API-02+ pendentes)
**Versão de contrato:** `API_CONTRACT_VERSION = "1.0"`
**Estado actual:** **API-01 CONCLUÍDA** (fundação contract-first com transporte stdlib + health). Os recursos de domínio (system, hardware, runtime, capabilities, models, tasks, knowledge, execution) entram por unidades API-02+.

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

O núcleo do WSAI 2 sabe decidir — mas precisa de ser **exposto** de forma estável a consumidores: uma futura interface de utilizador, comandos, scripts ou outras aplicações.

> A API é uma camada de apresentação (Constituição, artigo 6), **não** o centro da arquitectura. Expõe capacidades reais através de contratos estáveis.

O problema que a Fase 10 resolve é criar essa fronteira sem antecipar todo o catálogo de recursos e sem apoiar a camada na lógica central de negócio.

## 2. A ESTRATÉGIA (API-01)

A primeira unidade tomou uma **decisão arquitectural material**: estratégia **contract-first** com **transporte stdlib**.

```text
Pedido (ApiRequest)
  → ApiGateway (porte injectável)
  → StdLibHttpGateway (transporte http.server, sem dependências externas)
  → Resposta (ApiResponse)
```

### O que foi criado

- **`ApiRequest` / `ApiResponse`** — mensagens puras e imutáveis;
- **`ApiGateway`** — porte de transporte injectável;
- **`StdLibHttpGateway`** — adapter sobre `http.server` (JSON; 404/405 antes de qualquer handler; **zero dependências novas**);
- **serviço de exemplo `health`** — devolve as versões de contrato do núcleo e da API.

### A fronteira

```text
api → core   (apenas via wsai2.core.public — regra KERNEL-08)
```

A API **não contém** lógica central de decisão: expõe as superfícies públicas do núcleo. O `api` saiu de `SUBSISTEMAS_FUTUROS` na fonte única de contratos — fica `("ui",)`.

## 3. O CATÁLOGO FUTURO (API-02+)

O roadmap prevê, por unidade, os recursos que serão expostos:

```text
API-02  System
API-03  Hardware
API-04  Runtime
API-05  Capabilities
API-06  Models
API-07  Tasks
API-08  Knowledge
API-09  Execution / Status
API-10  API Integration Gate
```

Cada recurso entrará com **arestas específicas justificadas** na fonte única — o crescimento da API é controlado, nunca antecipado.

## 4. CONEXÃO COM A VISÃO

>A visão coloca a camada "API / Presentation" na arquitectura em camadas, com a regra: "as dependências devem apontar para dentro. O domínio não depende da API." E reforça: "a interface apresenta informação real produzida pelos serviços internos."

A Fase 10 é essa camada: expõe o que o núcleo **realmente** produz, atrás de contratos estáveis, e fica pronta para ser consumida pela UI (Fase 11). A comunicação com a futura UI também passa pelos contratos de use-case da camada Application (Ramo A — APP-02).

## 5. EVIDÊNCIA E VALIDAÇÃO

- `tests/test_api_gateway.py` (6 testes): contrato imutável; health 200; 404; 405; handle directo; health puro.
- Suíte completa no fecho: **513/513 verdes**.
- Frente de fronteira: `api` na fonte única, no `FIREWALL` e nas superfícies congeladas do kernel.

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: expor as capacidades do núcleo de forma estável, sem deixar a API virar o centro do sistema.
2. Solução: contract-first com transporte stdlib — porta injectável + adapter HTTP sem dependências externas.
3. A API consome o núcleo `apenas` através de `wsai2.core.public`; não contém lógica de negócio.
4. Estado: API-01 (fundação + health) concluída; os recursos (hardware, runtime, modelos, tarefas, conhecimento, execução) entram por unidades próprias.
5. É a ponte para a Fase 11 (UI), que apresenta a informação real produzida pelos serviços internos.