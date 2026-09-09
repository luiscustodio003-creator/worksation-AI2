---
description: Validar módulos, integrações e a fundação do WSAI 2 através de um gate formal e não destrutivo
agent: plan
---
# /wsai-validate — FOUNDATION VALIDATION GATE

Executar validação estruturada sem introduzir alterações funcionais.

## Contrato arquitectural

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`.

Em `TRANSITION`, validar também a segurança da migração: consumidores, dependências, fronteiras, compatibilidade, rollback e ausência de violações do Dependency Firewall.

## Modos

```text
/wsai-validate module <nome>
/wsai-validate integration
/wsai-validate foundation
/wsai-validate full
```

## Regra fundamental

VALIDAR NÃO É IMPLEMENTAR.

Não criar, apagar, mover ou refactorizar código funcional para fazer a validação passar.

## Pré-flight

1. `AGENTS.md`.
2. `PROJECT_STATE.md`.
3. `ROADMAP.md`.
4. arquitectura e contratos.
5. Command Execution Contract.
6. árvore real.
7. Git sem modificar.
8. módulos, testes, documentação e dependências.

## Áreas

### Inventário

Distinguir IMPLEMENTADO, PARCIAL, AUSENTE e NÃO APLICÁVEL.

### Arquitectura

Verificar fronteiras, dependências, imports proibidos, ciclos, duplicações, ownership e contratos.

### Migração

Quando aplicável verificar:

- classificação da alteração;
- consumidores migrados;
- origem preservada até validação;
- destino funcional;
- rollback possível;
- ausência de dependências proibidas.

### Código e contratos

Verificar responsabilidades, interfaces públicas, erros, lifecycle, timeout, cancellation, cleanup e estado.

### Testes

Executar unitários, integração, negativos, regressão e testes arquitecturais aplicáveis.

### Documentação

Comparar código ↔ testes ↔ documentação ↔ comandos ↔ estado persistente.

## Classificação

```text
P0 — crítico
P1 — alto
P2 — médio
P3 — baixo
```

`APPROVED` exige evidência suficiente e ausência de P0/P1/P2 bloqueantes. `APPROVED WITH WARNINGS` permite apenas P3.

## Foundation Gate

A aprovação é um estado formal de governação, não um pedido de confirmação. Dentro de `/wsai-run`, o resultado deve ser consumido automaticamente.

Se houver decisão arquitectural material nova, marcar `NOT APPROVED` e parar o ciclo.

## Relatório

Quando aplicável, actualizar `docs/validation/FOUNDATION_VALIDATION_REPORT.md` com data, commit, branch, inventário, arquitectura, contratos, testes, migração, documentação, problemas e decisão.

## Resultado

```text
RESULTADO: APPROVED | APPROVED WITH WARNINGS | NOT APPROVED
PRÓXIMO PASSO: ...
```

Não declarar aprovação apenas porque os testes passaram.
