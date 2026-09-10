# WSAI DEVELOPMENT SKILL

## Objectivo

Esta skill governa o desenvolvimento incremental do WorkStation AI 2. Não substitui a arquitectura do produto. Garante trabalho coerente, verificável, observável e sincronizado com o estado real do código.

## Fontes de verdade

A implementação real do repositório e os testes têm precedência sobre documentação desactualizada. Cruzar sempre código, testes, `PROJECT_STATE.md`, `ROADMAP.md`, arquitectura/constituição, estado de execução e Git.

`docs/project/RUN_GOVERNANCE.md` define as regras persistentes de continuidade, dependências e freeze do `/wsai-run`.

## Kernel fechado

O Kernel/Core está **CONSOLIDADO / FROZEN** conforme `docs/architecture/CORE_KERNEL_TARGET.md` e `docs/validation/KERNEL_CONSOLIDATION_REPORT.md`.

O desenvolvimento normal NÃO pode adicionar novas responsabilidades ao Kernel.

Antes de qualquer proposta de alteração no Kernel, classificar a necessidade:

```text
BUG | REGRESSION | SECURITY | CONTRACT VIOLATION | REQUIREMENT CHANGE | NEW CAPABILITY
```

`NEW CAPABILITY` não é motivo para reabrir o Kernel. Deve ser encaminhada para Application, Infrastructure, Capability, API, UI ou Addon conforme a responsabilidade.

## Visibilidade obrigatória

Durante qualquer comando de desenvolvimento deve ser possível identificar no fluxo visível:

- ramo;
- fase;
- unidade;
- etapa;
- estado;
- concluído;
- pendente;
- próximo passo.

Usar blocos de progresso em mudanças relevantes; não inventar percentagens.

## Sequência obrigatória

1. inspeccionar o directório;
2. ler `AGENTS.md`;
3. ler `PROJECT_STATE.md`;
4. consultar `ROADMAP.md`;
5. consultar `RUN_GOVERNANCE.md`;
6. consultar arquitectura e contratos aplicáveis;
7. verificar Git;
8. identificar ramo e unidade actual;
9. identificar dependências;
10. auditar responsabilidades existentes;
11. seleccionar estratégia/modelo adequado;
12. implementar apenas a unidade autorizada;
13. criar/actualizar testes;
14. executar validação da unidade;
15. executar gates aplicáveis;
16. rever alterações;
17. actualizar documentação;
18. actualizar estado persistente;
19. produzir relatório;
20. sincronizar Git quando permitido;
21. congelar a unidade concluída;
22. determinar a próxima unidade/ramo.

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

## Modelo de execução por ramo

Cada ramo é uma sequência de unidades pequenas e verificáveis.

```text
BRANCH
  -> UNIT
      -> AUDIT
      -> PLAN
      -> ARQ
      -> IMPLEMENT
      -> TEST
      -> VALIDATE
      -> DOC
      -> GIT
      -> FREEZE UNIT
  -> NEXT UNIT
  -> BRANCH COMPLETE
  -> BRANCH FROZEN
  -> DEPENDENCY GATE
  -> NEXT READY BRANCH
```

Quando todas as unidades de um ramo estiverem concluídas sem bloqueios, o ramo é fechado e congelado. Não reabrir automaticamente.

## Estados persistentes

O Run deve preservar, no mínimo:

```text
active_branch
branch_status
active_unit
unit_status
current_step
last_completed_step
next_action
blocked_reason
dependencies_checked
frozen_units
frozen_branches
last_commit
```

Uma nova chamada a `/wsai-run` retoma o primeiro trabalho incompleto a partir desse estado; não reinicia uma unidade já concluída.

## Dependências entre ramos

A ordem do roadmap não é suficiente para assumir dependência.

Antes de mudar de ramo, verificar contratos, gates e dependências reais. Se o próximo ramo estiver pronto, avançar. Se estiver bloqueado, parar, guardar o estado e indicar o bloqueio.

Ramos independentes podem ser executados sem criar dependências artificiais. Ramos dependentes só iniciam depois de os requisitos upstream estarem satisfeitos.

## Escopos do /wsai-run

```text
/wsai-run
```
Executa o próximo trabalho autorizado pelo estado persistente.

```text
/wsai-run fase <X>
```
Executa autonomamente o ramo/fase indicado, unidade a unidade, até concluir o ramo ou encontrar um bloqueio real.

O Run não deve ultrapassar o escopo solicitado para iniciar outro ramo sem que a política de transição o autorize.

## Regra de autorização

Uma unidade prevista no `PROJECT_STATE.md`/`ROADMAP.md`, com dependências satisfeitas e sem decisão arquitectural material nova, está autorizada para execução.

Dentro do `/wsai-run`, `READY TO IMPLEMENT` é suficiente. Não introduzir uma aprovação humana adicional entre planear e implementar.

`APPROVED` e `APPROVED WITH WARNINGS` são estados de gate, não pedidos de confirmação humana.

## Auditoria antes de expansão

Antes de `CREATE`, localizar primeiro:

- responsabilidade equivalente;
- contrato existente;
- serviço existente;
- adapter/facade reutilizável;
- consumidores;
- testes;
- documentação.

Preferência:

```text
REUSE -> ADAPT -> WRAP/ADAPTER -> EXTEND -> CREATE
```

Não criar módulos paralelos para uma responsabilidade já existente.

## Validação e qualidade

VALIDAR NÃO É IMPLEMENTAR. `/wsai-validate` confirma o estado sem alterar código funcional.

Uma aprovação considera comportamento, contratos, fronteiras, integração, recuperação, segurança e consistência documental, não apenas contagem de testes.

Ciclo formal:

```text
AUDIT → PLAN → ARQ → IMPLEMENT → TEST → VALIDATE → DOC → GIT
```

O ciclo pode repetir-se automaticamente para correcções seguras relacionadas com a unidade.

## Paragem obrigatória

Parar quando existir:

- decisão arquitectural material;
- requisito fundamental alterado;
- risco significativo de perda/corrupção de dados;
- conflito Git inseguro;
- falha técnica sem solução segura;
- dependência não satisfeita;
- violação do Dependency Firewall;
- tentativa de introduzir nova responsabilidade no Kernel.

Correcções P2 documentais/processuais inequívocas, localizadas e sem impacto funcional/arquitectural podem ser tratadas autonomamente e revalidadas.

## Freeze e reabertura

Uma unidade validada, documentada e sincronizada fica `COMPLETE` e `FROZEN`.

Um ramo com todas as unidades `FROZEN` passa a `BRANCH COMPLETE / FROZEN`.

Só reabrir por:

```text
REGRESSION
BUG
SECURITY ISSUE
FAILED INTEGRATION
REQUIREMENT CHANGE
DEPENDENCY CHANGE
```

A reabertura reinicia o ciclo completo e termina num novo freeze.

## Critério de conclusão

Uma unidade só é concluída com implementação adequada ao âmbito, testes, validação, documentação, estado persistente e Git coerente/verificável.

Um ramo só é concluído quando todas as suas unidades estão concluídas e sem bloqueios.

O projecto só pode ser marcado como concluído quando todos os ramos previstos estiverem fechados/frozen e não existir trabalho pendente autorizado.

## Relatório obrigatório

Cada conclusão relevante deve indicar:

- ramo e fase;
- unidade;
- o que foi implementado;
- reutilização realizada;
- enquadramento arquitectural;
- módulos/dependências;
- testes;
- problemas/prioridades;
- validação;
- estado do ramo;
- freeze;
- próximo ramo/unidade;
- eventual bloqueio.
