# WSAI DEVELOPMENT SKILL

## Objectivo

Esta skill governa o desenvolvimento incremental do WorkStation AI 2. Não substitui a arquitectura do produto. Garante trabalho coerente, verificável, observável e sincronizado com o estado real do código.

## Fonte de verdade operacional

A implementação real do repositório tem precedência sobre documentação desactualizada. Cruzar sempre código, testes, `PROJECT_STATE.md`, `ROADMAP.md`, arquitectura/constituição e Git.

## Visibilidade obrigatória

Durante qualquer comando de desenvolvimento deve ser possível identificar no fluxo visível: fase, unidade, etapa, concluído, pendente e próximo passo. Usar blocos de progresso em mudanças relevantes; não inventar percentagens.

## Sequência obrigatória

1. inspeccionar o directório;
2. ler `AGENTS.md`;
3. ler `PROJECT_STATE.md`;
4. consultar `ROADMAP.md`;
5. consultar arquitectura;
6. verificar Git;
7. identificar unidade actual;
8. identificar dependências;
9. auditar responsabilidades existentes;
10. seleccionar estratégia/modelo adequado;
11. implementar apenas a unidade autorizada;
12. criar/actualizar testes;
13. executar validação da unidade;
14. executar `/wsai-validate` quando existir gate;
15. rever alterações;
16. actualizar documentação;
17. actualizar estado;
18. produzir relatório;
19. sincronizar Git quando permitido.

## Família oficial de comandos

```text
/wsai
/wsai-run
/wsai-audit
/wsai-plan
/wsai-implement
/wsai-test
/wsai-validate
/wsai-doc
/wsai-git
```

`/wsai-run` é a composição autónoma destas responsabilidades. Os comandos individuais mantêm as suas próprias regras quando executados isoladamente.

## Regra de autorização dentro do /wsai-run

Uma unidade explicitamente prevista no `PROJECT_STATE.md`/`ROADMAP.md`, sem decisão arquitectural material nova, está autorizada para execução pelo `/wsai-run`.

Dentro do `/wsai-run`, `READY TO IMPLEMENT` é suficiente para avançar. Não introduzir uma aprovação humana adicional entre planear e implementar.

Um gate `APPROVED` é consumido pelo orquestrador como autorização para a transição definida no roadmap. Não é uma pergunta ao utilizador.

Um `NOT APPROVED` deve ser classificado. P0/P1, decisão arquitectural material, mudança de requisitos fundamentais, risco de perda de dados ou conflito Git não resolvível interrompem. P2 documental/processual inequívoco, localizado e sem impacto funcional/arquitectural pode ser corrigido autonomamente pelo `/wsai-run` através de uma unidade mínima e revalidado.

## Auditoria antes de expansão

Antes de criar novo módulo, registry, manager ou abstraction: localizar equivalentes, verificar fronteiras, consumidores, testes e documentação. Preferir evolução aditiva e reversível.

## Validação e qualidade

VALIDAR NÃO É IMPLEMENTAR. `/wsai-validate` confirma o estado sem alterar código funcional. Uma aprovação considera comportamento, contratos, fronteiras, integração, recuperação, segurança e consistência documental, não apenas contagem de testes.

Ciclo formal:

```text
AUDIT → PLAN → IMPLEMENT → TEST → VALIDATE → DOC → GIT
```

No `/wsai-run`, o ciclo pode repetir-se automaticamente para correcções seguras e para a próxima unidade autorizada.

## Autonomia controlada e continuidade

Depois de concluir, validar, documentar e sincronizar uma unidade, determinar novamente a próxima unidade a partir de `PROJECT_STATE.md` e `ROADMAP.md`.

Se estiver claramente definida, directamente dependente e não introduzir decisão arquitectural material, **DEVE continuar automaticamente no mesmo `/wsai-run`**. Não terminar apenas para mostrar "PRÓXIMA UNIDADE".

Se uma fase formal for aprovada:

```text
GATE APPROVED
↓
PROJECT_STATE actualizado
↓
ROADMAP consultado
↓
PRÓXIMA UNIDADE determinada
↓
PLAN → IMPLEMENT → TEST → VALIDATE → DOC → GIT
```

Parar apenas perante uma condição real de bloqueio ou decisão humana necessária.

## Critério de conclusão de uma base

Uma base só é concluída com implementação completa do âmbito, testes adequados, validação, documentação, relatório, estado arquitectural actualizado e Git coerente/verificável.

## Relatório obrigatório

Cada conclusão relevante deve indicar o que foi implementado, enquadramento arquitectural, finalidade, módulos/dependências, testes, problemas/prioridades, validação, estado da fase e próximo passo.
