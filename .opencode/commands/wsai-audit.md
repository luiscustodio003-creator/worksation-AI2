---
description: Auditar o estado real antes de alterar o WorkStation AI 2
agent: plan
---
# /wsai-audit — AUDITORIA CONTROLADA

Executar uma auditoria sem alterar código funcional.

## Contrato arquitectural

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`.

A auditoria deve determinar o estado real e, em migração `TRANSITION`, mapear explicitamente responsabilidades, consumidores, dependências, contratos e destino arquitectural. Não assumir que a estrutura física actual representa o target.

## Procedimento

1. Ler `AGENTS.md`.
2. Ler `PROJECT_STATE.md` e `ROADMAP.md`.
3. Ler arquitectura e contratos relevantes.
4. Inspeccionar árvore real.
5. Procurar responsabilidades já implementadas.
6. Verificar testes e documentação.
7. Verificar Git sem modificar.
8. Mapear dependências e consumidores.
9. Comparar código ↔ testes ↔ documentação.
10. Classificar requisitos como IMPLEMENTADO, PARCIAL, INTEGRAÇÃO NECESSÁRIA, AUSENTE ou NÃO NECESSÁRIO.

## Regra de segurança

Não criar, apagar, mover ou refactorizar código funcional durante a auditoria.

Se encontrar uma necessidade estrutural, classificar a alteração (`CREATE/ADAPT/MOVE/SPLIT/MERGE/DEPRECATE/DELETE/FREEZE`) e encaminhar para `/wsai-plan`.

## Resultado

```text
WSAI 2 — AUDITORIA
Área: ...
Estado arquitectura: LEGACY | TRANSITION | TARGET | FROZEN
Estado actual: ...
Responsabilidades existentes: ...
Consumidores: ...
Dependências: ...
Tipo de alteração sugerida: ...
Testes: ...
Documentação: ...
Problemas: P0 | P1 | P2 | P3
Risco: BAIXO | MÉDIO | ALTO
Recomendação: ...
```

A auditoria é uma fotografia do estado real. Não inventar componentes futuros como se já existissem.
