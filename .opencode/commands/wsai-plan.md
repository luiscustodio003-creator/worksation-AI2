---
description: Planear uma unidade WSAI 2 sem iniciar a implementação
agent: plan
---
# /wsai-plan — PLANEAMENTO CONTROLADO

Planear a unidade `$ARGUMENTS` sem implementar código funcional.

## Pré-condição

Usar a auditoria disponível. Se a unidade não estiver auditada, executar primeiro uma análise equivalente e registar as lacunas.

## Plano obrigatório

1. Objectivo e critério de conclusão.
2. Estado actual e componentes que já fornecem a responsabilidade.
3. Ficheiros que precisam de ser alterados.
4. Ficheiros novos estritamente necessários.
5. Interfaces/contratos envolvidos.
6. Dependências e direcção das dependências.
7. Impacto no `wsai-run` e no fluxo sequencial.
8. Compatibilidade com comandos `/wsai-*` individuais.
9. Estratégia de migração não destrutiva.
10. Estratégia de rollback.
11. Testes unitários, integração e regressão.
12. Documentação a actualizar.
13. Alterações ao `PROJECT_STATE.md`/`IMPLEMENTATION_LOG.md`.
14. Alterações Git previstas.
15. Riscos e condições de paragem.

## Regra especial

Não propor a criação de um novo módulo quando uma responsabilidade equivalente já existir. Preferir extensão, adapter ou integração sobre a substituição.

## Resultado

Entregar um plano executável por uma unidade pequena e verificável. Se a unidade for demasiado grande, dividi-la antes da implementação.
