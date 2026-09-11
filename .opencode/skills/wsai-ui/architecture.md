# WSAI 2 — UI Skill: Architecture Reference

## Camadas do WSAI 2

```
Utilizador
    │
    ▼
Interface (wsai2.interfaces.web)    ← esta skill
    │
    │  fetch("/api/...")
    │
    ▼
API (wsai2.api)                     ← Ramo B, COMPLETE / FROZEN
    │
    ▼
Application (wsai2.application)     ← Ramo A, COMPLETE / FROZEN
    │
    ▼
Core (wsai2.core)                   ← KERNEL, FROZEN
```

## Princípios Arquitecturais da UI

1. **Adapter Layer**: a UI adapta a experiência do utilizador aos
   contratos de API. Não contém lógica de negócio.
2. **Contratos primeiro**: cada funcionalidade da UI consome um
   contrato de API documentado.
3. **Independência do motor**: a UI não escolhe modelos, não decide
   roteamento, não conhece providers.
4. **Sidebar fixa**: navegação estável; o conteúdo muda.
5. **Barra de estado**: feedback discreto de CPU/RAM/Modelo/Status.
6. **Extensibilidade**: novas vistas entram pela sidebar; addons
   podem registar vistas.

## Vista por Defeito: Chat

O WSAI 2 abre na vista de Chat, com prompt central e chips de acção.
As restantes vistas (Browser, Projectos, Modelos, Runtime, Tarefas,
Addons, Definições) são acessíveis pela sidebar.

## Comunicação com a API

Todas as chamadas são `fetch()` para rotas `/api/*`.
- GET para leitura.
- POST com body JSON para mutations.
- Erros 4xx/5xx tratados pela UI e apresentados ao utilizador.
- Loading states: spinner ou skeleton.
- Polling para `/system` (barra de estado): cada 5s.

## Tecnologias

- HTML5 semântico (SPA).
- CSS custom (sem framework externo).
- JavaScript vanilla (ES2022+).
- SVG sprite inline (Feather-style).
- Fetch API + contratos HTTP.
- Futuro: WebSocket/SSE para streaming.