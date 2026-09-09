---
description: Planear uma unidade WSAI 2 sem iniciar a implementação
agent: plan
---
# /wsai-plan — PLANEAMENTO CONTROLADO

Planear a unidade `$ARGUMENTS` sem implementar código funcional quando executado isoladamente.

## CONTRATO DE ARQUITECTURA

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md` antes de planear alterações estruturais.

Durante a migração do Kernel, considerar `TRANSITION`. O plano deve trabalhar sobre responsabilidades e contratos, não assumir que a localização física actual de um módulo é definitiva.

Para qualquer alteração estrutural, declarar:

```text
Tipo: CREATE | ADAPT | MOVE | SPLIT | MERGE | DEPRECATE | DELETE | FREEZE
```

Aplicar `BEFORE EXTEND`: verificar primeiro se a responsabilidade já existe e preferir reutilização/adaptação/adapter.

## Pré-condição

Usar a auditoria disponível. O plano deve ser baseado no estado real do código, testes, documentação e Git.

## MODO ISOLADO VS. /WSAI-RUN

Isoladamente, termina em `READY TO IMPLEMENT` ou `BLOCKED`.

Dentro de `/wsai-run`, `READY TO IMPLEMENT` é autorização operacional suficiente quando a unidade está autorizada pelo estado/roadmap e não introduz decisão arquitectural material.

## Plano obrigatório

1. Objectivo e critério de conclusão.
2. Estado actual e responsabilidades já existentes.
3. Classificação da alteração.
4. Consumidores e dependências.
5. Ficheiros afectados e novos estritamente necessários.
6. Interfaces/contratos.
7. Direcção das dependências e Dependency Firewall.
8. Impacto nos comandos e no `/wsai-run`.
9. Estratégia de migração não destrutiva.
10. Estratégia de rollback.
11. Testes unitários, integração, negativos e regressão.
12. Critérios de validação.
13. Gate necessário.
14. Documentação e estado a actualizar.
15. Alterações Git.
16. Riscos e condições de paragem.

## Regras de migração

Para `MOVE`, `SPLIT`, `MERGE` ou `DELETE`, o plano deve demonstrar consumidores conhecidos e ordem segura de migração. Não planear remoção da origem antes de validar o destino.

Não propor estrutura nova artificial. Não transformar intenção futura em implementação.

## Resultado

```text
READY TO IMPLEMENT
```

ou

```text
BLOCKED
Motivo: ...
Decisão necessária: ...
```
