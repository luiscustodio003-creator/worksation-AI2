---
name: wsai-ui
description: Use when implementing, modifying or reviewing WSAI 2 UI components (index.html, app.js, style.css), Browser integration, or any code under src/wsai2/interfaces/. Also use when migrating code from the legacy WSAI repository (worksation-AI) into WSAI2. Do NOT use for Core, API, Application or infrastructure code.
---

# WSAI 2 — UI Skill

Skill operacional para implementação da camada de apresentação do WSAI 2.

## ANTES DE IMPLEMENTAR QUALQUER COISA NA UI

1. Ler `docs/architecture/WSAI2_UI_UX_ARCHITECTURE.md` — filosofia,
   layout, princípios, comunicação UI→API.
2. Ler `docs/architecture/WSAI2_BROWSER_ARCHITECTURE.md` — se o trabalho
   envolver o Browser integrado.
3. Ler `docs/architecture/WSAI2_UI_LEGACY_MIGRATION.md` — política de
   migração do WSAI antigo, mapeamento de endpoints, regras.
4. Inspeccionar UI existente do WSAI antigo em
   `D:\Dev\Python\WorkStation AI\interfaces\web\` (index.html, app.js,
   style.css) — apenas para referência visual, NUNCA copiar lógica.
5. Identificar contratos de API disponíveis em `docs/api/BASE-45..64`.
6. Confirmar que o endpoint que pretende usar existe e está testado.

## REGRAS OBRIGATÓRIAS

1. A UI é uma **Adapter Layer** — fala apenas com `wsai2.api` via HTTP.
2. **Nunca importar** módulos internos (core, application, etc.) na UI.
3. **Nunca copiar** `app.js` do WSAI antigo — reescrever funcionalidade
   por funcionalidade, consumindo contratos WSAI 2.
4. **HTML/CSS/SVG** do WSAI antigo são reutilizáveis (com adaptações).
5. Cada componente da UI deve ter um **teste de integração** com a API.
6. A sidebar mantém-se como constante visual — o conteúdo da área
   principal é que muda.
7. A barra de estado (inferior) usa `GET /system` com polling de 5s.
8. O Browser é um addon/capacidade — não é funcionalidade monolítica.
9. Tecnologias: HTML5 + CSS + JavaScript vanilla (ES2022+). Sem React,
   Vue, Angular ou frameworks externos.
10. Comentários em código e docs em **PT de Portugal**.

## ESTRUTURA DE DIRECTÓRIOS

```
src/wsai2/
└── interfaces/
    └── web/
        ├── index.html
        └── static/
            ├── app.js
            └── style.css
```

## MAPA DE ENDPOINTS (API_CONTRACT_VERSION 1.0)

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

## CICLO DE TRABALHO

Para cada componente da UI:

1. **AUDIT**: verificar se o endpoint de API existe; ler contrato.
2. **PLAN**: definir DOM, estados, eventos, chamadas de API.
3. **IMPLEMENT**: escrever HTML/CSS/JS; adapter para API.
4. **TEST**: teste de integração (mock ou real).
5. **VALIDATE**: confirmar que sidebar + barra de estado funcionam.
6. **DOC**: actualizar documentação se relevante.
7. **GIT**: commit unitário + push.

## REFERÊNCIAS

- `docs/architecture/WSAI2_UI_UX_ARCHITECTURE.md`
- `docs/architecture/WSAI2_BROWSER_ARCHITECTURE.md`
- `docs/architecture/WSAI2_UI_LEGACY_MIGRATION.md`
- `docs/api/BASE-45-api-contract-foundation.md` até `BASE-64`
- `D:\Dev\Python\WorkStation AI\interfaces\web\` (UI antiga — referência)