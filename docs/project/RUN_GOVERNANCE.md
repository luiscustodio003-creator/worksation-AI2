# WSAI2 — RUN GOVERNANCE

## Objectivo

Definir a governação persistente do `/wsai-run` depois do fecho do Kernel, permitindo desenvolvimento autónomo controlado, reutilização do código existente, continuidade, dependências, freeze e retoma segura.

## Princípio fundamental

O Kernel está **CONSOLIDADO / FROZEN**. O `/wsai-run` não reabre o Kernel para acrescentar novas capacidades.

Uma alteração ao Kernel só pode ser considerada quando existir uma correcção comprovada, regressão, vulnerabilidade, violação de contrato ou outra falha que torne o estado actual incorrecto. Nova funcionalidade deve ser colocada na camada adequada: Application, Infrastructure, Capability, API, UI ou Addon.

## Ciclo obrigatório de uma unidade

```text
AUDIT
  -> PLAN
  -> ARQ
  -> IMPLEMENT
  -> TEST
  -> VALIDATE
  -> DOC
  -> GIT
  -> FREEZE UNIT
  -> NEXT
```

O `/wsai-run` compõe os comandos individuais existentes e não cria regras paralelas para cada etapa.

## Estados da unidade

```text
PENDING
AUDIT
PLANNED
ARCHITECTURE
IMPLEMENTING
TESTING
VALIDATING
DOCUMENTING
GIT
COMPLETE
BLOCKED
```

Uma unidade `COMPLETE` fica congelada. Não deve ser reaberta automaticamente.

## Estados do ramo

```text
READY
IN_PROGRESS
BLOCKED
COMPLETE
FROZEN
```

`COMPLETE` implica que todas as unidades do ramo foram validadas. Depois do fecho, o ramo passa a `FROZEN`.

## Reabertura controlada

Um ramo `FROZEN` só pode ser reaberto por uma causa explícita:

- regressão;
- bug comprovado;
- falha de integração;
- vulnerabilidade;
- alteração material de requisitos;
- alteração incompatível de uma dependência.

A reabertura cria novamente um ciclo de auditoria, planeamento, implementação, testes, validação, documentação e Git, terminando num novo freeze.

## Dependências entre ramos

Os ramos são independentes por defeito apenas quando a arquitectura e os contratos demonstrarem que não existe dependência impeditiva.

Antes de iniciar outro ramo, o `/wsai-run` deve verificar:

1. estado do ramo;
2. unidades concluídas;
3. gates necessários;
4. contratos requeridos;
5. dependências upstream;
6. ausência de bloqueios conhecidos.

Se a dependência estiver satisfeita, o ramo pode iniciar. Se não estiver, o ramo fica `BLOCKED` e o estado é persistido.

## Fecho e transição

Quando a última unidade de um ramo termina sem erros:

```text
UNIT COMPLETE
  -> BRANCH COMPLETE
  -> BRANCH FROZEN
  -> CHECK DEPENDENCIES
  -> SELECT NEXT READY BRANCH
```

O ramo seguinte não é escolhido apenas pela posição no ficheiro. Deve ser compatível com as dependências reais.

Se não houver outro ramo pronto, o `/wsai-run` termina com `WAITING FOR DEPENDENCY` e indica exactamente o bloqueio.

Quando todos os ramos previstos estiverem `FROZEN` e não existir trabalho pendente no roadmap, o estado global pode ser marcado `ROADMAP COMPLETE`.

## Reutilização antes de criação

Antes de `CREATE`, procurar sempre:

- responsabilidade equivalente;
- contrato já existente;
- adapter/facade reutilizável;
- serviço existente;
- teste existente;
- documentação existente.

Preferência:

```text
REUSE -> ADAPT -> WRAP/ADAPTER -> EXTEND -> CREATE
```

Criar um novo módulo exige justificação de que a responsabilidade não existe já ou não pode ser reutilizada sem violar uma fronteira.

## Estado persistente

O estado operacional deve conservar pelo menos:

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

A fonte de verdade do trabalho continua a ser a combinação de código/testes, `PROJECT_STATE.md`, `ROADMAP.md`, arquitectura e Git. Este documento define apenas as regras de governação do Run.

## Escopo de execução

```text
/wsai-run
```
Executa o próximo trabalho autorizado a partir do estado persistente.

```text
/wsai-run fase <X>
```
Executa o ramo/fase indicado, unidade a unidade, até ao fim do ramo ou até surgir um bloqueio real.

Uma execução não deve ultrapassar o escopo explicitamente solicitado quando isso implicar entrar num ramo não autorizado.

## Regra de segurança

Nunca sacrificar integridade arquitectural para manter continuidade automática. Autonomia significa continuar quando a próxima acção é conhecida, segura, reversível e verificável; não significa ultrapassar uma decisão arquitectural material.
