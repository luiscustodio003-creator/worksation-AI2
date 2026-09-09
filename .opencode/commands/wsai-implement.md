---
description: Implementar uma unidade WSAI 2 previamente planeada
agent: build
---
# /wsai-implement — IMPLEMENTAÇÃO CONTROLADA

Implementar apenas a unidade `$ARGUMENTS` definida pela auditoria e pelo plano actual.

## CONTRATO DE TRANSIÇÃO

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`.

Durante `TRANSITION`, preservar comportamento validado e trabalhar por unidades pequenas e reversíveis.

Antes de editar, confirmar:

- `AGENTS.md`;
- estado persistente;
- arquitectura/contratos;
- branch e Git;
- consumidores dos componentes afectados;
- classificação `CREATE/ADAPT/MOVE/SPLIT/MERGE/DEPRECATE/DELETE/FREEZE`.

## Regras

1. Integrar antes de substituir.
2. Criar apenas o estritamente necessário.
3. Não duplicar responsabilidades.
4. Respeitar Core/Application/Infrastructure/Addons.
5. Addon usa apenas Core Public API.
6. Core não depende de Addons/Application.
7. Não introduzir dependências desnecessárias.
8. Criar/actualizar testes na mesma unidade.
9. Não declarar concluído sem validação.

## Migração segura

```text
estado actual
    ↓
mapeamento de consumidores
    ↓
adapter/integração compatível, se necessário
    ↓
migração
    ↓
testes + validação
    ↓
remoção posterior da origem, apenas se segura
```

Para `MOVE`, `SPLIT`, `MERGE` ou `DELETE`, não remover a origem antes de demonstrar que o destino funciona e que os consumidores foram migrados.

## Protecção do wsai-run

Se afectar comandos, contratos ou governação, preservar execução autónoma, continuidade, progresso visível, paragem segura e estado persistente.

## Resultado

Indicar ficheiros alterados, classificação da alteração, testes, validação, riscos residuais e próximo passo. Documentação/Git seguem as etapas próprias, salvo dependência inseparável definida no plano.
