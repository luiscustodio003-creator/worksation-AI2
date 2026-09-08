---
description: Orquestrar autonomamente uma unidade completa de desenvolvimento WSAI 2
---
# /wsai-run — ORQUESTRADOR AUTÓNOMO DO WORKSTATION AI 2

## Missão

Executar a próxima unidade lógica de desenvolvimento do WorkStation AI 2 de forma controlada, respeitando a arquitectura, a documentação, os testes e o estado do repositório.

`/wsai-run` é um **orquestrador de execução**, não um comando de consulta. Depois de determinar a próxima unidade válida, deve executar o ciclo completo até concluir a unidade, atingir um bloqueio real ou encontrar uma decisão arquitectural que exija intervenção humana.

## VISIBILIDADE OBRIGATÓRIA DA EXECUÇÃO

A autonomia do `/wsai-run` **não pode eliminar a observabilidade**. O utilizador deve conseguir saber, durante toda a execução, **em que fase está, qual unidade está a ser executada, o que já foi concluído, o que está em curso e qual é o próximo passo**.

No início da execução e sempre que houver mudança de fase ou etapa relevante, apresentar um bloco curto de progresso no fluxo visível do agente, usando este formato:

```text
╔══════════════════════════════════════════════════╗
║ WSAI 2 — PROGRESSO                               ║
╠══════════════════════════════════════════════════╣
║ Fase:      ...                                   ║
║ Unidade:   ...                                   ║
║ Etapa:     ...                                   ║
║ Progresso: ██████░░░░ ...%                       ║
║                                                  ║
║ ✓ concluído                                      ║
║ ● em execução                                    ║
║ ○ pendente                                       ║
║                                                  ║
║ Próximo: ...                                     ║
╚══════════════════════════════════════════════════╝
```

Durante operações demoradas, actualizar o progresso em pontos significativos. Não produzir mensagens a cada comando trivial.

A visibilidade de progresso é obrigatória mesmo quando a unidade é executada autonomamente e mesmo quando a próxima fase já está determinada. O relatório final continua a usar a estrutura da FASE I.

O progresso mostrado deve reflectir o estado real e nunca inventar percentagens. Se uma etapa ainda não puder ser quantificada, usar `EM EXECUÇÃO`.

## FAMÍLIA DE COMANDOS WSAI

`/wsai-run` é o orquestrador completo. As etapas também estão disponíveis individualmente:

```text
/wsai-audit
/wsai-plan
/wsai-implement
/wsai-test
/wsai-validate
/wsai-doc
/wsai-git
```

Quando `/wsai-run` executa autonomamente, deve seguir as mesmas regras e critérios definidos para essa família.

## AUTORIDADE DE EXECUÇÃO E APROVAÇÃO

`/wsai-run` é responsável por executar o ciclo quando a unidade já está autorizada pelo `PROJECT_STATE.md`/`ROADMAP.md` e não existe uma nova decisão arquitectural material.

Uma saída `READY TO IMPLEMENT` de `/wsai-plan` é suficiente para o `/wsai-run` prosseguir quando:

- a unidade já está prevista no estado/roadmap;
- o plano não introduz uma decisão arquitectural material;
- não existe P0/P1/P2 funcional que exija redefinição do âmbito;
- a implementação é reversível e verificável.

**Não solicitar aprovação humana adicional para um plano interno que cumpra estes critérios.**

Se `/wsai-validate` devolver `NOT APPROVED` por uma lacuna **documental ou processual P2** que seja inequívoca, localizada e sem impacto funcional/arquitectural, `/wsai-run` deve tratar essa lacuna como uma unidade correctiva do mesmo gate: planear, corrigir, testar quando aplicável, revalidar e continuar. Não deve ficar preso num ciclo de aprovação humana.

Só uma decisão arquitectural material, mudança de requisitos fundamentais, risco de perda de dados, conflito Git não resolvível ou falha técnica sem solução segura constitui motivo para pedir intervenção humana.

## Entrada

Quando o utilizador executar:

```text
/wsai-run
```

não assumir que o projecto está vazio nem que a fase anterior foi concluída.

## REGRA FUNDAMENTAL DE EXECUÇÃO AUTÓNOMA

Depois de determinar a próxima unidade lógica em `PROJECT_STATE.md`/`ROADMAP.md`, o agente **DEVE avançar automaticamente para o planeamento, implementação, validação, documentação e sincronização dessa unidade**.

**NÃO deve parar apenas porque conseguiu identificar ou apresentar a "PRÓXIMA UNIDADE".**

O ciclo só pode terminar quando ocorrer uma destas condições:

1. a unidade foi concluída, validada, documentada e sincronizada;
2. existe uma falha técnica real que não pode ser resolvida autonomamente com segurança;
3. existe conflito/divergência Git que não pode ser resolvido com segurança;
4. é necessária uma decisão arquitectural nova e material que não esteja definida na documentação existente;
5. existe alteração de requisitos fundamentais ou risco significativo que exija decisão humana.

Uma unidade claramente definida no estado persistente **não requer confirmação do utilizador para começar**.

## FASE A — PRE-FLIGHT

Inspeccionar:

1. directório actual;
2. estrutura do projecto;
3. `AGENTS.md`;
4. `docs/project/PROJECT_STATE.md`;
5. `docs/project/ROADMAP.md`;
6. documentação arquitectural;
7. configuração OpenCode disponível;
8. estado Git;
9. testes existentes.

Apresentar o primeiro bloco `WSAI 2 — PROGRESSO` depois de identificar o contexto inicial.

## FASE B — SINCRONIZAÇÃO

Verificar o estado Git antes de alterar ficheiros.

Sempre que o ambiente permitir:

```text
git status
git branch --show-current
git remote -v
git fetch --all --prune
```

Não sobrescrever alterações locais ou remotas sem compreender a situação.

## FASE C — DETERMINAÇÃO DA PRÓXIMA UNIDADE

A decisão deve basear-se em:

- fase actual;
- estado persistente;
- roadmap;
- dependências concluídas;
- testes existentes;
- documentação.

Nunca seleccionar uma unidade que dependa de uma base ainda inexistente.

Depois de determinar a unidade, **a execução deve prosseguir imediatamente para a FASE D**. Não produzir um relatório final nesta fase.

### Regra de transição de gate

Quando uma fase formal for aprovada, a transição é determinística:

```text
FOUNDATION APPROVED
↓
actualizar PROJECT_STATE.md
↓
consultar ROADMAP.md
↓
determinar próxima unidade
↓
executar automaticamente a próxima unidade
```

`APPROVED`, `APPROVED WITH WARNINGS` e uma decisão de fecho de fase documentada **não são pedidos de confirmação ao utilizador**. São estados de governação consumidos pelo orquestrador.

## FASE D — PLANEAMENTO INTERNO

Antes de modificar código, identificar:

- objectivo da unidade;
- módulos afectados;
- novos ficheiros necessários;
- dependências;
- testes;
- documentação;
- riscos.

O planeamento é interno e serve para iniciar a execução. Não deve ser tratado como resultado final nem como motivo para parar.

Se a unidade for apenas uma correcção documental/processual necessária para fechar um gate, o plano deve permanecer mínimo e não criar componentes funcionais.

## FASE E — IMPLEMENTAÇÃO

Implementar de acordo com `AGENTS.md`, constituição arquitectural, skill `wsai-development`, responsabilidade única e compatibilidade Windows/Linux quando aplicável.

Não criar uma estrutura artificialmente complexa. Antes de criar uma nova responsabilidade, verificar se já existe uma implementação equivalente.

Se durante a implementação forem encontrados problemas menores e solucionáveis sem alterar a arquitectura, corrigi-los autonomamente e continuar.

Actualizar o bloco de progresso ao entrar na implementação e ao terminar uma alteração relevante.

## FASE F — VALIDAÇÃO

Executar os testes aplicáveis.

Se existirem falhas corrigíveis relacionadas com a unidade, **DEVE tentar corrigi-las e voltar a executar a validação** antes de terminar.

Se um gate formal devolver `NOT APPROVED`, classificar cada bloqueio. P0/P1, decisão arquitectural material ou ambiguidade de requisitos interrompem o ciclo. P2 documental/processual inequívoco deve regressar ao ciclo correctivo e ser resolvido autonomamente quando estiver dentro do âmbito já autorizado.

Actualizar o bloco de progresso ao iniciar os testes, ao corrigir falhas e ao concluir a validação.

## FASE G — DOCUMENTAÇÃO E ESTADO

Actualizar, conforme aplicável:

- documentação do módulo;
- `PROJECT_STATE.md`;
- `IMPLEMENTATION_LOG.md`;
- relatório específico da base concluída.

O relatório deve explicar o que foi feito, enquadramento arquitectural, dependências, testes, estado da fase e próximo passo.

**`PROJECT_STATE.md` deve ser actualizado para reflectir a unidade realmente concluída antes do relatório final.**

## FASE H — GIT E SINCRONIZAÇÃO

Depois da validação:

1. inspeccionar `git diff`;
2. confirmar ficheiros modificados;
3. verificar se a alteração representa uma unidade coerente;
4. criar commit descritivo quando permitido;
5. efectuar push para o remoto quando as credenciais e o ambiente o permitirem;
6. verificar novamente o estado.

Nunca esconder uma falha de sincronização.

## FASE I — RESULTADO FINAL

No final produzir:

```text
╔══════════════════════════════════════════════════╗
║ WSAI 2 — RESULTADO DA UNIDADE                   ║
╚══════════════════════════════════════════════════╝

✓ Unidade: ...
✓ Arquitectura: ...
✓ Implementação: ...
✓ Testes: ...
✓ Documentação: ...
✓ Git: ...
✓ GitHub: ...

ESTADO DA ARQUITECTURA
...

PRÓXIMA UNIDADE
...
```

A secção `PRÓXIMA UNIDADE` é calculada **depois** de actualizar `PROJECT_STATE.md`. Serve para informar e orientar a continuação do ciclo.

## REGRA DE CONTINUIDADE ENTRE UNIDADES

Depois de concluir, validar, documentar e sincronizar uma unidade, o agente deve avaliar a próxima unidade.

Se estiver claramente definida, directamente dependente, pequena ou suficientemente especificada e não introduzir decisão arquitectural material, **DEVE continuar automaticamente no mesmo `/wsai-run`**, em vez de terminar apenas com "PRÓXIMA UNIDADE".

Se a próxima unidade introduzir uma decisão arquitectural material, deve concluir a unidade actual, actualizar toda a documentação e parar com um relatório claro indicando a decisão necessária.
