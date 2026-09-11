# WSAI 2 — UI Skill: Migration Reference

## Origem

Repositório: `luiscustodio003-creator/worksation-AI`

```
interfaces/web/
├── index.html      (~27 KB)  — SPA completa
└── static/
    ├── app.js      (~93 KB)  — lógica + chamadas API
    └── style.css   (~33 KB)  — estilos
```

## Categorias de Tratamento

### A — REUTILIZAR
Layout HTML, CSS, SVG sprite, sidebar, diálogos, chips, conversas UI,
projectos UI, loading states, responsive CSS.

### B — ADAPTAR
`mostrarVista()`, `carregarSistema()`, `carregarEstadoLLM()`,
`listarProjectos()`, `listarConversas()`, `carregarTelemetria()`,
`carregarBenchmark()`, `carregarDIL()`, `perguntarDIL()`,
`ligarEnterParaEnviar()`, toast/notificações.

### C — NÃO MIGRAR
Chamadas directas a endpoints antigos, lógica de negócio no frontend,
acesso ao Core/Engine, decisões de modelo/routing, configuração de
threads/SIMD, lógica de inferência/providers.

## Mapeamento de Endpoints

| Antigo                        | WSAI 2                          |
|-------------------------------|----------------------------------|
| `GET /api/saude`              | `GET /health`                    |
| `GET /api/hardware`           | `GET /hardware`                  |
| `GET /api/metrics`            | `GET /runtime` + `GET /system`   |
| `GET /api/benchmark`          | `POST /tasks` (kind: benchmark) |
| `GET /api/llm/estado`         | `GET /models` (activo)           |
| `GET /api/projectos`          | BRANCH F (Projects)              |
| `POST /api/development/ask`   | `POST /tasks`                    |

## Ordem de Migração

1. Layout base (UI-01)
2. Dashboard (UI-02)
3. Hardware (UI-03) → `GET /hardware`
4. Modelos (UI-04) → `GET /models`
5. Capabilities (UI-05) → `GET /capabilities`
6. Tarefas (UI-06) → `POST /tasks`
7. Runtime (UI-07) → `GET /runtime`
8. Knowledge (UI-08) → `POST /knowledge`
9. Execution (UI-09) → `POST /executions`
10. UI Gate (UI-10)

## Regras

1. Nunca copiar `app.js` — reescrever por funcionalidade.
2. Reutilizar HTML/CSS quando adequado.
3. Preservar SVG sprite.
4. Sem dependências externas (React, Vue, etc.).
5. Testar cada componente após adaptação.
6. Contratos primeiro — confirmar endpoint antes de código.