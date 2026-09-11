# WSAI 2 — Browser Architecture

## Responsabilidade

Definir a arquitectura do Browser integrado do WSAI 2: uma vista de
navegação web integrada na UI, onde o Browser é uma **capacidade do
sistema** (não uma aplicação separada) e a assistência AI aparece como
parte integrada da experiência.

## 1. Filosofia

```
Browser → Contexto/Intenção → Application → Capability → Execution → Model
```

- O Browser **nunca decide** qual modelo utilizar.
- O Browser fornece **contexto e intenção** à camada Application.
- A Application decide como processar (regra WSAI2: UI não tem lógica
  de negócio).
- A assistência AI aparece **inline** no Browser, não como popup ou
  aplicação separada.

## 2. Layout

```
┌───────────────┬────────────────────────────────────────────────┐
│               │ ← → ⟳  🔍 endereço / pesquisa                  │
│ WSAI 2        ├────────────────────────────────────────────────┤
│               │                                                │
│ + Novo        │                                                │
│               │                                                │
│ Projectos     │              CONTEÚDO WEB                       │
│ Browser   ←   │                                                │
│ Modelos       │                                                │
│ Runtime       │         ┌──────────────────────┐               │
│ Tarefas       │         │  PAINEL AI (lateral)  │               │
│ Addons        │         │  Contexto da página   │               │
│               │         │  Sugestões            │               │
│               │         │  Resumo               │               │
│ Conversas     │         └──────────────────────┘               │
│               │                                                │
└───────────────┴────────────────────────────────────────────────┘
```

O painel AI é um overlay lateral activável quando o utilizador pretende
assistência sobre a página actual. Pode ser retraído.

## 3. Componentes

### 3.1 Barra de Navegação

- Botões: Voltar, Avançar, Actualizar.
- Campo de endereço/pesquisa (URL ou query).
- Indicador de estado (a carregar, seguro, erro).

### 3.2 Área de Conteúdo (WebView/iframe)

- Renderiza a página web solicitada.
- Para sites que bloqueiam iframe, fornece extração de conteúdo via
  backend (`POST /tasks` com contexto "extrair conteúdo de URL").

### 3.3 Painel AI Lateral (activável)

- **Contexto da página**: título, descrição, conteúdo extraído.
- **Sugestões contextuais**: baseadas no conteúdo e na intenção do
  utilizador.
- **Resumo AI**: pedido via `POST /tasks` com contexto da página.
- **Ações**: "Pesquisar sobre...", "Extrair dados...", "Analisar...",
  que são submetidas como tarefas à Application.

### 3.4 Sidebar (mantém-se)

A sidebar do WSAI 2 mantém-se visível durante a navegação, com a vista
Browser activa (item sublinhado na sidebar).

## 4. Integração com o WSAI 2

### 4.1 Contratos Utilizados

| Rota                | Método | Utilização no Browser                          |
|---------------------|--------|------------------------------------------------|
| `/tasks`            | POST   | Submeter tarefa com contexto da página         |
| `/knowledge`        | POST   | Pesquisar knowledge com base no conteúdo       |
| `/executions`       | POST   | Submeter execução (extrair dados, analisar)    |
| `/executions/status`| POST   | Ver estado da tarefa submetida                 |
| `/executions/cancel`| POST   | Cancelar tarefa em curso                       |

### 4.2 Fluxo de Assistência AI

```
Utilizador navega para uma página
    │
    ▼
Browser carrega conteúdo
    │
    ▼
Utilizador activa Painel AI (click)
    │
    ▼
Browser envia contexto para Application
    │  POST /knowledge  (pesquisar sobre o tema da página)
    │  POST /tasks      (solicitar resumo/extração)
    │
    ▼
Application processa via Core
    │
    ▼
Resultado apresentado no Painel AI
```

### 4.3 Fluxo de Extração de Dados

```
Utilizador: "Extrair dados desta tabela"
    │
    ▼
Browser: POST /executions { kind: "extraction", context: { url, content } }
    │
    ▼
Application: ExecutionService.execute(...)
    │
    ▼
Browser: POST /executions/status { execution_id } (polling até concluir)
    │
    ▼
Resultado apresentado no Painel AI
```

## 5. Extração de Conteúdo

O Browser precisa de obter o conteúdo das páginas para alimentar a AI.
Estratégias:

1. **iframe directo**: para sites que permitem (sem `X-Frame-Options`).
2. **Proxy backend**: `GET /system` ou endpoint futuro de proxy web —
   o backend faz fetch da página e devolve HTML/texto extraído.
3. **Extract via tasks**: quando o Browser detecta que a página não é
   acessível via iframe, usa `POST /tasks` com o URL para o backend
   extrair e processar.

Na fase inicial (UI-01 a UI-05), o Browser usa iframe + proxy backend.
A extração inteligente entra na fase avançada.

## 6. Segurança

1. O Browser não tem acesso directo a `file://` ou recursos locais.
2. Cookies e sessões de sites visitados são isolados (sandbox de iframe).
3. Downloads são geridos pelo backend, não pelo Browser directamente.
4. O conteúdo extraído é processado pelo backend antes de ser apresentado
   à AI — sanitização de XSS.

## 7. Roadmap de Implementação

| Fase  | Unidade    | Âmbito                                          |
|-------|------------|-------------------------------------------------|
| 1     | UI-01      | Vista Browser básica (iframe + barra de endereço)|
| 2     | UI-08      | Knowledge integrado no Browser (pesquisa)        |
| 3     | ADDON-01   | Browser como addon (extensível)                  |
| 4     | Futuro     | Painel AI lateral completo                       |
| 5     | Futuro     | Extração inteligente de conteúdo                 |
| 6     | Futuro     | Downloads e histórico                            |

## 8. Diferenças Face ao WSAI Antigo

O WSAI antigo não tinha Browser integrado. O Browser do WSAI 2 é uma
**capacidade nova** que entra como addon, não como funcionalidade monolítica.

A abordagem é: Browser como adapter que consome contratos de API,
da mesma forma que Chat, Projectos ou Modelos.

## Referências

- `WSAI2_UI_UX_ARCHITECTURE.md` — arquitectura geral da UI.
- `WSAI2_UI_LEGACY_MIGRATION.md` — política de migração.
- `docs/api/BASE-64-api-integration-gate.md` — contratos da API.