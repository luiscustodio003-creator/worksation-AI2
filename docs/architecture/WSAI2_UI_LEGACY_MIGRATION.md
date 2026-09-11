# WSAI 2 — UI Legacy Migration Policy

## Responsabilidade

Definir a política de migração do código da camada de apresentação do
WSAI antigo (`worksation-AI`) para o WSAI 2, garantindo que se reutiliza
o que é válido sem transportar a arquitectura monolítica antiga para o
novo Core.

## 1. Origem do Material

Repositório de origem: `luiscustodio003-creator/worksation-AI`

```
interfaces/
└── web/
    ├── index.html          (~27 KB)  — SPA completa
    └── static/
        ├── app.js          (~93 KB)  — lógica de UI + chamadas API
        └── style.css       (~33 KB)  — estilos e layout
```

Backend (referência):
```
interfaces/
└── api/
    ├── app.py              — FastAPI server
    ├── schemas.py          — schemas Pydantic
    └── routers/
        ├── chat.py         — chat + LLM
        ├── hardware.py     — hardware info
        ├── modelos.py      — loja de modelos
        ├── projects.py     — projectos
        ├── runtime.py      — runtime info
        ├── capabilities.py — capabilities
        ├── documentos.py   — documentos
        ├── monitoring.py   — telemetria
        ├── benchmark.py    — benchmark
        ├── pipeline.py     — pipeline
        ├── development.py  — DIL/dev
        ├── compat.py       — compatibilidade
        ├── saude.py        — health
        └── inference_config.py — configuração de inferência
```

## 2. Categorias de Tratamento

### A — REUTILIZAR (directamente)

| Elemento         | Origem           | Notas                                             |
|------------------|------------------|---------------------------------------------------|
| Layout HTML      | index.html       | Estrutura semântica, sidebar, abas, diálogos      |
| CSS              | style.css        | Layout, cores, tipografia, responsividade         |
| SVG sprite       | index.html       | Ícones Feather-style, sem dependências externas   |
| Sidebar          | index.html       | Estrutura fixa com navegação lateral              |
| Diálogos/Modais  | index.html       | Overlays de projecto, novo projecto, etc.         |
| Chips            | index.html       | Componentes visuais de acção rápida               |
| Conversas UI     | index.html       | Lista de conversas, pesquisa, filtros             |
| Projectos UI     | index.html       | Vista de projecto, ficheiros, instruções          |
| Loading states   | style.css        | Skeleton, spinner, fade-in                        |
| Responsive CSS   | style.css        | Breakpoints e media queries                       |

### B — ADAPTAR (requer reescrita pontual)

| Elemento                | Origem         | Tratamento WSAI 2                                       |
|-------------------------|----------------|----------------------------------------------------------|
| `mostrarVista(nome)`    | app.js         | Adaptar para novo router de vistas (Chat/Browser/etc.)  |
| `carregarSistema()`     | app.js         | Mapear para `GET /system` + `GET /hardware`             |
| `carregarEstadoLLM()`   | app.js         | Mapear para `GET /models` (modelo activo)               |
| `listarProjectos()`     | app.js         | Mapear para contrato futuro de projectos (BRANCH F)     |
| `listarConversas()`     | app.js         | Mapear para contrato futuro de conversas                |
| `carregarTelemetria()`  | app.js         | Mapear para `GET /runtime` + `GET /system`              |
| `carregarBenchmark()`   | app.js         | Adaptar para `POST /tasks` com kind "benchmark"         |
| `carregarDIL()`         | app.js         | Adaptar para `POST /tasks` com kind "development"       |
| `perguntarDIL()`        | app.js         | Mapear para `POST /tasks`                               |
| `ligarEnterParaEnviar()`| app.js         | Reutilizar lógica; adaptar para novo DOM                |
| Toast/notificações      | app.js         | Reutilizar padrão; adaptar para novos contextos         |

### C — NÃO MIGRAR (proibido)

| Elemento                         | Razão                                        |
|----------------------------------|----------------------------------------------|
| Chamadas directas a endpoints    | Usa contratos WSAI 2 em vez de rotas antigas|
| Lógica de negócio no frontend    | Toda a lógica fica no backend                |
| Acesso directo ao Core/Engine    | UI fala apenas com a API                     |
| Decisões de modelo/routing       | Application decide, UI apresenta             |
| Gestão de estado do motor        | Vem de `GET /runtime` e `GET /system`        |
| Configuração de threads/SIMD     | Configuração é do backend                     |
| Lógica de inferência             | Está no `wsai2.runtime_engine`               |
| Lógica de providers             | Está no `wsai2.provider`                      |
| Estado de execução no frontend   | Estado é do backend; UI faz polling          |

## 3. Mapeamento de Endpoints Antigos → Contratos WSAI 2

| Endpoint antigo                  | Contrato WSAI 2               |
|----------------------------------|-------------------------------|
| `GET /api/saude`                 | `GET /health`                 |
| `GET /api/hardware`             | `GET /hardware`               |
| `GET /api/metrics`              | `GET /runtime` + `GET /system`|
| `GET /api/benchmark`            | `POST /tasks` (kind: benchmark)|
| `GET /api/llm/estado`          | `GET /models` (activo)        |
| `GET /api/projectos`           | Futuro: BRANCH F (Projects)   |
| `GET /api/projectos/{id}`      | Futuro: BRANCH F               |
| `POST /api/projectos`          | Futuro: BRANCH F               |
| `GET /api/projectos/{id}/conversas`| Futuro: BRANCH F           |
| `GET /api/conversas`           | Futuro: BRANCH F               |
| `DELETE /api/conversas/{id}`   | Futuro: BRANCH F               |
| `POST /api/development/ask`    | `POST /tasks`                  |
| `GET /api/development/*`       | `POST /tasks` / `GET /runtime`|

## 4. Estrutura Alvo no WSAI 2

```
src/wsai2/
│
├── core/
├── application/
├── api/
│
└── interfaces/
    └── web/
        ├── index.html          ← reutilizado do WSAI antigo (adaptado)
        └── static/
            ├── app.js          ← reescrito (consome contratos WSAI 2)
            ├── style.css       ← reutilizado do WSAI antigo (adaptado)
            └── ...
```

A pasta `interfaces/web/` é servida pelo `StdLibHttpGateway` do WSAI 2
ou por servidor HTTP estático separado. A UI nunca faz parte do Core.

## 5. Regras de Migração

1. **Nunca copiar `app.js` tal como está** — reescrever funcionalidade
   por funcionalidade, consumindo contratos WSAI 2.
2. **Reutilizar HTML/CSS** sempre que a estrutura visual for adequada;
   adaptar apenas o que for necessário para o novo layout.
3. **Preservar SVG sprite** — os ícones Feather-style são independentes
   e reutilizáveis.
4. **Não importar dependências externas** (React, Vue, etc.) — manter
   vanilla JS + HTML + CSS conforme o padrão do projecto.
5. **Testar cada componente** individualmente após adaptação.
6. **Manter a sidebar fixa** como constante visual; mudar apenas o
   conteúdo da área principal.
7. **Contratos primeiro** — antes de escrever código, confirmar que o
   endpoint de API existe e está documentado em BASE-45..64.

## 6. Ordem de Migração Sugerida

| Fase | Componente    | Dependência         | Unidade  |
|------|---------------|---------------------|----------|
| 1    | Layout base   | Nenhuma             | UI-01    |
| 2    | Dashboard     | Layout              | UI-02    |
| 3    | Hardware      | `GET /hardware`     | UI-03    |
| 4    | Modelos       | `GET /models`       | UI-04    |
| 5    | Capabilities  | `GET /capabilities` | UI-05    |
| 6    | Tarefas       | `POST /tasks`       | UI-06    |
| 7    | Runtime       | `GET /runtime`      | UI-07    |
| 8    | Knowledge     | `POST /knowledge`   | UI-08    |
| 9    | Execution     | `POST /executions`  | UI-09    |
| 10   | UI Gate       | Todos anteriores    | UI-10    |

Cada fase: migrar componente → testar → validar com API real → documentar.

## 7. Verificação de Integridade

Antes de cada commit de UI:

1. A UI apenas chama `/api/*` — nunca importa módulos internos.
2. Cada chamada `/api/*` corresponde a um contrato existente.
3. A sidebar mantém-se funcional durante a migração.
4. Não há `TODO`/`NotImplementedError` em código de produção.
5. CSS não quebra layout existente.

## Referências

- `WSAI2_UI_UX_ARCHITECTURE.md` — arquitectura geral da UI.
- `WSAI2_BROWSER_ARCHITECTURE.md` — arquitectura do Browser.
- `docs/api/BASE-64-api-integration-gate.md` — contratos da API.
- Repositório de origem: `luiscustodio003-creator/worksation-AI`.