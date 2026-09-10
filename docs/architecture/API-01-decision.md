# WORKSTATION AI 2 — REGISTO DE DECISÃO: NEXT-ARCHITECTURE-DECISION

## Data

2026-09-10

## Unidade destinatária

Fase 10 — API (subsistema `wsai2.api`); decisão material que desbloqueia a
camada Application.

## Contexto

A sequência KERNEL-01..10 foi consolidada em `main` (KERNEL-CONSOLIDATION-CLOSE,
`fa7b41f`). Três vias seguintes competiam por decisão: Fase 10 — API, addon
Projects (1º consumidor do contrato de addon) e enriquecimento semântico da
Fase 9 (embeddings). A via escolhida foi **Fase 10 — API**.

Justificação (estado real): o hosting de addons não existe por desígnio
(BASE-33: "sem bootstrap antecipado"); Projects como 1º consumidor exigiria
primeiro maquinaria de alojamento (antecipação). As embeddings exigem decisão
de modelo/fornecedor dependente de externa. A API é a única via roadmapped
(Fase 10) sem dependências prévias não resolvidas: os contratos de todos os
domínios existem e o kernel está fechado.

## Decisões

### 1. Via — Fase 10 (API)

Criar a camada Application `wsai2.api` que expõe as capacidades reais do
sistema através de contratos estáveis (arquitectura 3.10). Autorizado pelo
utilizador em `/wsai-plan NEXT-ARCHITECTURE-DECISION`.

### 2. Estratégia de transporte — contract-first, stdlib

A API é **contract-first**: `ApiRequest`/`ApiResponse` puros + porte
`ApiGateway` injectável. O primeiro transporte é um adapter de biblioteca
standard (`http.server`), sem dependências novas. Outros transportes (ex.:
ASGI) são adicionados como adaptadores, sem tocar nos handlers.

Justificação: coerência com o padrão de adaptadores/transportes injectáveis
do Provider; zero dependências externas; verificação sem rede e testes
deterministas; sub-stituibilidade futura barata.

### 3. Fronteira da API (regra contract)

- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08) na fundação.
- Recursos de domínio entram por unidades API-02+ com arestas específicas
  justificadas e cobertas por teste (hardware/runtime/capability/model/
  provider/task/knowledge).
- O domínio não conhece a API; a Application não contém lógica central de
  negócio (constituição, artigo 7).

### 4. Fora de âmbito (adiado por decisão)

- Addon Projects e eddoção de addons: permanecem futuros (alvo, sec. 9).
- Embeddings da Fase 9: decisão material terminal continua em aberto.
- UI (Fase 11): continua em `SUBSISTEMAS_FUTUROS`.

## Estado após a decisão

`SUBSISTEMAS_FUTUROS = ("ui",)`. `api` implementado na fundação (API-01),
versionado e autorizado. ROADMAP Fase 10 em curso.