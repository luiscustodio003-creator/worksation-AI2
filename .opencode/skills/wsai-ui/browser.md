# WSAI 2 — UI Skill: Browser Reference

## Filosofia do Browser

O Browser é uma **capacidade do WSAI 2**, não uma aplicação separada.
A assistência AI aparece **inline** no Browser.

```
Browser → Contexto/Intenção → Application → Capability → Execution
```

O Browser **nunca decide** qual modelo utilizar. Fornecer contexto à
Application.

## Layout do Browser

```
┌───────────────┬────────────────────────────────────────────────┐
│               │ ← → ⟳  🔍 endereço / pesquisa                  │
│ WSAI 2        ├────────────────────────────────────────────────┤
│               │                                                │
│ Browser   ←   │              CONTEÚDO WEB                       │
│               │                                                │
│               │         ┌──────────────────────┐               │
│               │         │  PAINEL AI (lateral)  │               │
│               │         └──────────────────────┘               │
└───────────────┴────────────────────────────────────────────────┘
```

## Componentes

1. **Barra de Navegação**: Voltar, Avançar, Actualizar, endereço.
2. **Área de Conteúdo**: iframe ou extração via backend.
3. **Painel AI**: contexto, sugestões, resumo — activável lateralmente.

## Contratos Utilizados

- `POST /tasks` — submeter tarefa com contexto da página.
- `POST /knowledge` — pesquisar knowledge com base no conteúdo.
- `POST /executions` — submeter execução (extrair, analisar).
- `POST /executions/status` — estado da tarefa.
- `POST /executions/cancel` — cancelar tarefa.

## Extração de Conteúdo

1. **iframe directo**: sites que permitem.
2. **Proxy backend**: backend faz fetch e devolve conteúdo.
3. **Extract via tasks**: `POST /tasks` com URL para extração.

## Segurança

- Sem acesso a `file://`.
- Sandbox de iframe.
- Downloads geridos pelo backend.
- Conteúdo sanitizado antes de AI.