---
description: Orquestrar autonomamente o desenvolvimento WSAI 2 por unidades e ramos congeláveis
---
# /wsai-run — ORQUESTRADOR AUTÓNOMO DO WORKSTATION AI 2

## Missão

Executar o trabalho autorizado do WorkStation AI 2 de forma autónoma, controlada, verificável e recuperável, respeitando arquitectura, contratos, testes, documentação, dependências e estado persistente.

O `/wsai-run` compõe `/wsai-audit`, `/wsai-plan`, `/wsai-implement`, `/wsai-test`, `/wsai-validate`, `/wsai-doc` e `/wsai-git`. Não duplicar as regras desses comandos.

## ESTADO ARQUITECTURAL ACTUAL

O Kernel/Core está **CONSOLIDADO / FROZEN**. Ler obrigatoriamente:

- `docs/architecture/CORE_KERNEL_TARGET.md`
- `docs/validation/KERNEL_CONSOLIDATION_REPORT.md`
- `docs/project/RUN_GOVERNANCE.md`
- `docs/project/PROJECT_STATE.md`
- `docs/project/ROADMAP.md`

A antiga migração do Kernel em estado `TRANSITION` está encerrada. Não tratar o projecto como `TRANSITION` salvo evidência documental posterior que determine uma reabertura controlada.

## PROTECÇÃO DO KERNEL

Antes de alterar qualquer coisa relacionada com o Kernel, classificar:

```text
BUG | REGRESSION | SECURITY | CONTRACT VIOLATION | REQUIREMENT CHANGE | NEW CAPABILITY
```

`NEW CAPABILITY` não autoriza expansão do Kernel. Encaminhar a responsabilidade para Application, Infrastructure, Capability, API, UI ou Addon.

Só uma falha real que torne o Kernel incorrecto pode justificar reabertura controlada. Nunca reabrir por preferência de desenho, optimização especulativa ou nova funcionalidade.

## REGRA BEFORE EXTEND

Antes de `CREATE`, procurar sempre responsabilidade equivalente e preferir:

```text
REUSE -> ADAPT -> WRAP/ADAPTER -> EXTEND -> CREATE
```

Inspeccionar consumidores, contratos, testes, fronteiras e documentação. Não criar módulos paralelos quando a responsabilidade já existir.

## VISIBILIDADE OBRIGATÓRIA

No início e em mudanças relevantes apresentar:

```text
WSAI 2 — PROGRESSO

Ramo:      ...
Fase:      ...
Unidade:   ...
Etapa:     ...
Estado:    ...

✓ concluído
● em execução
○ pendente

Próximo:   ...
```

Nunca inventar percentagens. Se não houver base mensurável, usar `EM EXECUÇÃO`.

## FASE A — PRE-FLIGHT

Inspeccionar:

1. estrutura real;
2. `AGENTS.md`;
3. `docs/project/PROJECT_STATE.md`;
4. `docs/project/ROADMAP.md`;
5. `docs/project/RUN_GOVERNANCE.md`;
6. arquitectura e constituição;
7. contratos aplicáveis;
8. estado Git;
9. testes existentes;
10. comandos/skills OpenCode relevantes.

## FASE B — SINCRONIZAÇÃO

Verificar:

```text
git status
git branch --show-current
git remote -v
git fetch --all --prune
```

Nunca sobrescrever alterações locais/remotas sem compreender a divergência. Não usar reset destrutivo nem force push como recuperação normal.

## FASE C — ESTADO E SELECÇÃO

Ler o estado persistente antes de seleccionar trabalho.

Determinar:

- ramo activo;
- fase;
- unidade activa;
- etapa actual;
- unidades concluídas;
- unidades congeladas;
- ramos congelados;
- dependências;
- bloqueios;
- próximo trabalho autorizado.

Se existir uma unidade incompleta, retomar essa unidade no primeiro passo pendente. Não reiniciar trabalho já concluído.

## ESCOPOS

### `/wsai-run`

Executar o próximo trabalho autorizado a partir do estado persistente.

### `/wsai-run fase <X>`

Executar o ramo/fase indicado, unidade por unidade, até:

1. todas as unidades do ramo estarem concluídas; ou
2. surgir um bloqueio real.

Não entrar automaticamente noutro ramo fora do escopo explícito.

## FASE D — CICLO DA UNIDADE

Cada unidade passa obrigatoriamente por:

```text
AUDIT
  ↓
PLAN
  ↓
ARQ
  ↓
IMPLEMENT
  ↓
TEST
  ↓
VALIDATE
  ↓
DOC
  ↓
GIT
  ↓
FREEZE UNIT
```

Uma unidade só passa a `COMPLETE / FROZEN` depois de evidência suficiente em todas as etapas aplicáveis.

## FASE E — CORRECÇÕES

Se testes ou validação detectarem falhas seguras e directamente relacionadas com a unidade, corrigir autonomamente e repetir o ciclo necessário.

Não expandir o âmbito para resolver problemas não relacionados.

## FASE F — FECHO DO RAMO

Depois de concluir uma unidade:

```text
UNIT COMPLETE
   ↓
SAVE STATE
   ↓
NEXT UNIT?
   ├── SIM → continuar
   └── NÃO → BRANCH COMPLETE
```

Quando todas as unidades do ramo estiverem `COMPLETE`:

```text
BRANCH COMPLETE
   ↓
BRANCH FROZEN
   ↓
CHECK NEXT BRANCH DEPENDENCIES
```

Não reabrir automaticamente um ramo congelado.

## FASE G — DEPENDENCY GATE

Antes de iniciar outro ramo, verificar:

- contratos necessários;
- gates upstream;
- dependências técnicas;
- estado dos ramos dependentes;
- ausência de bloqueios;
- compatibilidade arquitectural.

Se o próximo ramo estiver pronto:

```text
NEXT BRANCH READY
→ iniciar
```

Se estiver bloqueado:

```text
BRANCH BLOCKED
→ guardar estado
→ parar
→ indicar motivo e próxima acção
```

Não criar dependências artificiais apenas porque dois ramos aparecem próximos no roadmap.

## FASE H — FREEZE E REABERTURA

Unidade concluída:

```text
COMPLETE / FROZEN
```

Ramo totalmente concluído:

```text
COMPLETE / FROZEN
```

Reabrir apenas por:

```text
REGRESSION
BUG
SECURITY ISSUE
FAILED INTEGRATION
REQUIREMENT CHANGE
DEPENDENCY CHANGE
```

A reabertura exige nova auditoria, planeamento, arquitectura quando aplicável, implementação, testes, validação, documentação e Git, terminando num novo freeze.

## FASE I — DOCUMENTAÇÃO E ESTADO

Actualizar, conforme aplicável:

- documentação arquitectural;
- documentação do módulo;
- `PROJECT_STATE.md`;
- `ROADMAP.md`;
- `RUN_GOVERNANCE.md`;
- `IMPLEMENTATION_LOG.md`;
- relatórios de validação.

Persistir pelo menos:

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

## FASE J — GIT

Inspeccionar diff, confirmar âmbito, executar testes relevantes, confirmar documentação e criar commit coerente. Fazer push quando permitido.

## FASE K — RESULTADO

Produzir:

```text
WSAI 2 — RESULTADO

Ramo:      ...
Fase:      ...
Unidade:   ...

✓ Audit
✓ Plan
✓ Arq
✓ Implement
✓ Test
✓ Validate
✓ Doc
✓ Git
✓ Freeze

Estado do ramo: ...
Próxima unidade: ...
Próximo ramo: ...
Bloqueio: ...
```

## REGRA DE CONTINUIDADE

Depois de concluir uma unidade, determinar novamente a próxima a partir do estado real.

Se a próxima unidade estiver especificada, pronta, segura, reversível e sem decisão arquitectural material:

```text
CONTINUAR AUTOMATICAMENTE
```

Se estiver bloqueada ou exigir decisão material:

```text
PARAR
GUARDAR ESTADO
INDICAR PRÓXIMA ACÇÃO
```

Quando terminar o último item de um ramo, fechar e congelar o ramo antes de avaliar o próximo.

Quando todos os ramos previstos estiverem congelados e não existir trabalho autorizado pendente, marcar o roadmap como concluído apenas com evidência correspondente.

## PRINCÍPIO DE SEGURANÇA

Autonomia não significa alterar tudo o que parece melhor. O `/wsai-run` deve preservar o que já foi validado, reutilizar o código existente, respeitar fronteiras e parar perante decisões materiais. O objectivo é avançar sem estragar trabalho consolidado.
