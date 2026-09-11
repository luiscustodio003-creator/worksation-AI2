# WSAI 2 — UI Skill: UX Reference

## Layout

```
┌───────────────┬─────────────────────────────────────────────────┐
│               │                                                 │
│   Sidebar     │              Área de Conteúdo                    │
│  (240px)      │             (flex-grow: 1)                       │
│               │                                                 │
│               │                                                 │
├───────────────┴─────────────────────────────────────────────────┤
│ ● Status │ Modelo │ CPU │ RAM │ Tok/s │ Estado                  │
└─────────────────────────────────────────────────────────────────┘
```

## Sidebar

- **+ Novo**: nova conversa ou projecto.
- **Projectos**: lista/expansão de projectos.
- **Browser**: navegador integrado.
- **Modelos**: loja + modelo activo.
- **Runtime**: estado do motor.
- **Tarefas**: tarefas activas.
- **Addons**: addons/loja.
- **Definições**: configurações.
- **Conversas**: lista recente + pesquisa.

## Vista de Chat

Prompt central + chips de acção + canvas de conversa.
Mensagens em cards (utilizador / WSAI) com Markdown.

## Vista de Projecto

Abas: Detalhe / Ficheiros / Instruções / Conversas.
Botões: Editar, GitHub, Arquivar, Apagar.
Upload de ficheiros, ponto de situação via `/tasks`.

## Barra de Estado

Actualização a cada 5s via `GET /system`.
Click abre overlay de diagnóstico completo.

## Estados da UI

- **Idle**: sem tarefas; modelo disponível.
- **Loading**: aguardar resposta de API.
- **Streaming**: receber tokens (futuro).
- **Error**: mensagem amigável.
- **Offline**: backend indisponível.

## Principios de UX

1. Minimalismo visual.
2. Sidebar fixa.
3. Um contexto de cada vez.
4. Feedback discreto (barra inferior).
5. Progressive disclosure.
6. Responsividade ≥1024px.