---
description: Implementar uma unidade WSAI 2 previamente planeada
agent: build
---
# /wsai-implement — IMPLEMENTAÇÃO CONTROLADA

Implementar apenas a unidade `$ARGUMENTS` definida pela auditoria e pelo plano actual.

## Antes de editar

- Confirmar `AGENTS.md`, estado persistente e documentação relevante.
- Confirmar que a unidade está suficientemente definida.
- Confirmar a branch e o estado Git.
- Reavaliar ficheiros afectados se o estado do repositório tiver mudado.

## Regras

1. Preservar o comportamento funcional já validado.
2. Integrar antes de substituir.
3. Criar apenas os ficheiros estritamente necessários.
4. Respeitar as fronteiras Core/Application/Infrastructure.
5. Não duplicar registries, engines, contratos ou responsabilidades existentes.
6. Não introduzir dependências desnecessárias.
7. Manter compatibilidade Windows/Linux quando aplicável.
8. Criar/actualizar testes da unidade na mesma alteração.
9. Não declarar concluído sem validação.

## Migração segura

Quando uma responsabilidade existente precisar de evolução:

```text
implementação actual
        ↓
adapter/integração compatível
        ↓
nova capacidade
        ↓
testes de regressão
        ↓
remoção posterior de código obsoleto, se justificada
```

Não apagar a implementação anterior apenas para simplificar a estrutura.

## `wsai-run`

Se a unidade alterar componentes consumidos pelo `wsai-run`, preservar obrigatoriamente:

- execução autónoma;
- sequência lógica;
- progresso visível;
- paragem segura;
- relatório final;
- actualização de estado.

## Resultado

No final, indicar ficheiros alterados, testes criados/actualizados, riscos residuais e o próximo passo. A documentação e o Git são tratados pelas etapas próprias, salvo se o plano exigir uma alteração mínima inseparável.
