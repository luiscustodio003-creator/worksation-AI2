# WSAI 2 — UI Skill: Integration Reference

## Camada de Integração

A UI integra com o WSAI 2 exclusivamente via contratos HTTP.

```
UI (JavaScript)
    │
    │  fetch("/api/...")
    │
    ▼
wsai2.api (contratos)
    │
    ▼
wsai2.application (use-cases)
    │
    ▼
wsai2.core (serviços)
```

## Contratos Disponíveis

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

## Política de Chamadas

1. Todas as chamadas são `fetch()` para `/api/*`.
2. POST com body JSON para mutations; GET para leitura.
3. A UI trata erros 4xx/5xx e apresenta ao utilizador.
4. Loading states: spinner ou skeleton.
5. Polling para `/system`: cada 5s (barra de estado).

## Estados

- **Idle**: sem tarefas activas.
- **Loading**: aguardar resposta.
- **Streaming**: receber tokens (futuro).
- **Error**: mensagem amigável.
- **Offline**: backend indisponível.

## Eventos Internos

- Click/Teclado → acções de UI.
- Polling → actualizações de estado.
- Futuro: WebSocket/SSE para streaming.