# WSAI 2 — UI/UX Architecture

## Responsabilidade

Definir a arquitectura, princípios e estrutura da camada de apresentação
(Interface Layer) do WSAI 2, servindo de referência obrigatória para todas
as unidades do BRANCH C (UI).

A UI é uma **Adapter Layer** que comunica exclusivamente com o subsistema
`wsai2.api` (contratos `API_CONTRACT_VERSION 1.0`). Nunca acede directamente
ao Core, Application ou qualquer módulo interno.

## 1. Filosofia

```
Utilizador → Interface → API (contratos) → Application → Core
```

- **Contratos primeiro**: a UI consume apenas contratos de API documentados.
- **Sem lógica de negócio**: a UI apresenta, formata e encaminha; o backend
  decide.
- **Independência do motor**: a UI não escolhe modelos, não decide
  roteamento, não conhece providers.
- **Addons por cima**: Browser, PDF, OCR, RAG, Vision entram como
  capacidades via contratos, não como código colado no Core.

## 2. Princípios de UX

1. **Minimalismo visual**: interface limpa, sem excesso de ícones; o
   conteúdo ocupa praticamente todo o espaço.
2. **Sidebar fixa**: navegação estável à esquerda, sem reflow do conteúdo.
3. **Um contexto de cada vez**: o utilizador vê uma vista (Chat, Browser,
   Projecto, Runtime, etc.); a sidebar mantém-se.
4. **Feedback discreto**: estados de sistema (CPU/RAM/Modelo/Status) em
   barra inferior compacta, não no centro da interface.
5. **Progressive disclosure**: funcionalidades avançadas aparecem por
   contexto (点击 no item → painel/overlay), não na primeira camada.
6. **Responsividade**: layout adapta-se a ecrãs ≥1024px (desktop) com
   comportamento de fallback para ecrãs menores.

## 3. Layout Geral

```
┌───────────────┬─────────────────────────────────────────────────┐
│               │                                                 │
│    Sidebar    │              Área de Conteúdo                    │
│   (240px)     │             (flex-grow: 1)                       │
│               │                                                 │
│               │                                                 │
│               │                                                 │
│               │                                                 │
├───────────────┴─────────────────────────────────────────────────┤
│ ● Status │ Modelo │ CPU │ RAM │ Tok/s │ Estado                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.1 Sidebar (240px, fixa)

```
┌─────────────┐
│ WSAI 2      │
│             │
│ + Novo      │
│             │
│ Projectos   │
│ Browser     │
│ Modelos     │
│ Runtime     │
│ Tarefas     │
│ Addons      │
│ Definições  │
│ ──────────  │
│ Conversas   │
│  conversa 1 │
│  conversa 2 │
└─────────────┘
```

- **+ Novo**: cria conversa ou projecto (contexto dependente).
- **Projectos**: lista de projectos (activo: vista de projecto).
- **Browser**: navegador integrado (Ramo C fase avançada / ADDON).
- **Modelos**: loja de modelos e gestão de modelo activo.
- **Runtime**: estado do motor, contexto, performance.
- **Tarefas**: lista de tarefas activas e submetidas.
- **Addons**: addons activos e loja.
- **Definições**: configurações gerais.
- **Conversas**: lista de conversas recentes (com pesquisa e filtro por
  projecto).

### 3.2 Área de Conteúdo

Muda consoante a vista seleccionada na sidebar:

| Vista         | Conteúdo principal                                          |
|---------------|-------------------------------------------------------------|
| Chat          | Canvas de conversa + input de prompt + chips de acção        |
| Browser       | WebView integrada + barra de endereço + contexto AI          |
| Projectos     | Lista de projectos / vista de projecto (ficheiros, instruções) |
| Modelos       | Loja de modelos + modelo activo + detalhe de performance     |
| Runtime       | Estado do motor (CPU, RAM, tok/s, contexto, threads)        |
| Tarefas       | Lista de tarefas com estado (pendente, activa, concluída)   |
| Addons        | Lista de addons / loja                                       |
| Definições    | Configurações gerais                                         |

### 3.3 Barra de Estado (inferior)

```
────────────────────────────────────────────────────────────────
● WSAI Local │ Qwen 3B Q4_K_M │ CPU 38% │ RAM 4.7 GB │ Ready
────────────────────────────────────────────────────────────────
```

- Actualização periódica (polling a `GET /system` ou WebSocket futuro).
- Click abre overlay/painel de diagnóstico completo.
- Fonte de dados: contratos `GET /system`, `GET /hardware`, `GET /runtime`.

## 4. Vista de Chat

```
                    WSAI 2

             Como posso ajudar?

       ┌───────────────────────────────────┐
       │                                   │
       │  Escreva o que pretende fazer...  │
       │                                   │
       │                                   │
       │  +   Chat     Browser       Qwen  │
       └───────────────────────────────────┘
```

- **Prompt central**: textarea com suporte a Enter para enviar.
- **Chips de acção**: atalhos para tarefas comuns (submeter tarefa,
  pesquisar knowledge, analisar ficheiro).
- **Mensagens**: apresentação em cards (utilizador / WSAI) com suporte a
  Markdown, código, tabelas e streams.
- **Input**: textarea com upload de ficheiros (drag & drop), botão de
  envio e paragem.

## 5. Vista de Projecto

```
┌─────────────┬───────────────────────────────────────┐
│  Detalhe    │  Ficheiros    │  Instruções    │ Conv. │
├─────────────┴───────────────────────────────────────┤
│  Conteúdo da aba seleccionada                        │
└─────────────────────────────────────────────────────┘
```

- Abas: Detalhe / Ficheiros / Instruções / Conversas associadas.
- Botões de acção: Editar, GitHub (ligar/sincronizar), Arquivar, Apagar.
- Ficheiros: upload, preview, remoção.
- Ponto de situação: botão que pede `POST /tasks` com contexto do
  projecto e devolve um resumo.

## 6. Comunicação UI → API

```
UI (JavaScript/SPA)
    │
    │  fetch("/api/...")
    │
    ▼
wsai2.api (contratos HTTP)
    │
    ▼
wsai2.application (use-cases)
    │
    ▼
wsai2.core (serviços)
```

### Contratos disponíveis (API_CONTRACT_VERSION 1.0)

| Rota                         | Método | Use-case         |
|------------------------------|--------|------------------|
| `/health`                    | GET    | Sonda de saúde   |
| `/system`                    | GET    | SystemInfo       |
| `/hardware`                  | GET    | HardwareProfile  |
| `/runtime`                   | GET    | RuntimeProfile   |
| `/capabilities`              | GET    | Capabilities     |
| `/models`                    | GET    | Models           |
| `/tasks`                     | POST   | TaskAnalysis     |
| `/knowledge`                 | POST   | KnowledgeContext  |
| `/executions`                | POST   | Execution        |
| `/executions/status`         | POST   | ExecutionStatus  |
| `/executions/cancel`         | POST   | Cancellation     |

### Política de chamadas

1. Todas as chamadas são `fetch()` para rotas `/api/*`.
2. POST com body JSON para mutation; GET para leitura.
3. A UI trata erros 4xx/5xx e apresenta ao utilizador.
4. Loading states: spinner ou skeleton por defeito; optimistic updates
   quando apropriado.
5. Polling periódico para `/system` (barra de estado): cada 5s.

## 7. Estados e Eventos

### Estados da UI

- **Idle**: sem tarefas activas; modelo disponível.
- **Loading**: a aguardar resposta de API.
- **Streaming**: a receber tokens (quando suportado).
- **Error**: erro de API; mensagem amigável.
- **Offline**: backend indisponível; mensagem de reconexão.

### Eventos

A UI reage a eventos internos (click, teclado) e a estados de API.
Actualmente (fase inicial) usa polling; futuro: WebSocket/SSE para
streaming de tokens e actualizações de estado de execução.

## 8. Segurança

1. A UI não armazena chaves de API nem tokens no `localStorage`.
2. Autenticação (quando existir) é feita via cookies ou headers gerenciados
   pelo backend.
3. A UI não executa código arbitrário do utilizador; apresenta apenas
   resultados de API.
4. Upload de ficheiros: validação de tipo e tamanho no frontend e backend.

## 9. Extensibilidade

- Novas vistas são adicionadas à sidebar e ao mapa de rotas.
- Novos endpoints de API são consumidos por novos componentes da UI.
- Addons podem registar vistas na sidebar via contrato (futuro
  `wsai2.addon`).
- O Browser entra como addon com vista integrada (ver
  `WSAI2_BROWSER_ARCHITECTURE.md`).

## 10. Tecnologias

| Camada        | Tecnologia                            |
|---------------|---------------------------------------|
| Markup        | HTML5 semântico (SPA)                 |
| Estilo        | CSS custom (sem framework externo)    |
| Comportamento | JavaScript vanilla (ES2022+)          |
| Ícones        | SVG sprite inline (Feather-style)     |
| Transporte    | Fetch API + contratos HTTP            |
| Futuro        | WebSocket/SSE para streaming          |

Não se usa React, Vue, Angular ou qualquer framework SPA externo. A
camada de apresentação é leve e independente, alinhada com a filosofia
de modularidade do WSAI 2.

## Referências

- `WSAI2_BROWSER_ARCHITECTURE.md` — arquitectura do Browser integrado.
- `WSAI2_UI_LEGACY_MIGRATION.md` — política de migração do WSAI antigo.
- `docs/api/BASE-64-api-integration-gate.md` — contratos da API.
- `docs/architecture/ARCHITECTURE.md` — secção 3.10 (API Transport).