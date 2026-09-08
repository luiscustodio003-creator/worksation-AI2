# WSAI DEVELOPMENT SKILL

## Objectivo

Esta skill governa o desenvolvimento incremental do WorkStation AI 2.

Não substitui a arquitectura do produto. A sua função é garantir que o trabalho de desenvolvimento permanece coerente, verificável, observável e sincronizado com o **estado real do código**.

## Fonte de verdade operacional

A implementação real do repositório tem precedência sobre documentação desactualizada. Para determinar o estado actual, cruzar sempre:

1. código existente;
2. testes existentes;
3. `docs/project/PROJECT_STATE.md`;
4. `docs/project/ROADMAP.md`;
5. arquitectura e constituição;
6. Git.

Documentação não deve ser tratada como prova de que uma funcionalidade existe.

## Visibilidade obrigatória

A autonomia do agente não pode significar ausência de contexto para o utilizador. Durante qualquer comando de desenvolvimento, deve ser sempre possível identificar no fluxo visível do agente:

- fase actual;
- unidade actual;
- etapa em curso;
- trabalho já concluído;
- trabalho pendente;
- próximo passo.

No início do trabalho e em cada mudança relevante de etapa, apresentar um bloco curto de progresso. Em operações demoradas, actualizar em pontos significativos, sem gerar ruído por cada comando trivial.

Formato recomendado:

```text
WSAI 2 — PROGRESSO
Fase: ...
Unidade: ...
Etapa: ...
Progresso: ...
✓ concluído | ● em execução | ○ pendente
Próximo: ...
```

As percentagens só devem ser usadas quando forem sustentadas pelo estado real; caso contrário, usar um estado textual.

## Sequência obrigatória

Sempre que for iniciado trabalho através de um comando de desenvolvimento:

1. inspeccionar o directório do projecto;
2. ler `AGENTS.md`;
3. ler `PROJECT_STATE.md`;
4. consultar `ROADMAP.md`;
5. consultar a documentação arquitectural relevante;
6. verificar Git;
7. identificar a unidade de trabalho actual;
8. identificar dependências;
9. auditar responsabilidades existentes antes de criar módulos ou interfaces novos;
10. seleccionar uma estratégia e o modelo OpenCode adequado à complexidade;
11. implementar apenas a unidade de trabalho aprovada;
12. criar ou actualizar testes;
13. executar validação da unidade;
14. executar `/wsai-validate` quando o estado/planeamento definir um gate de consolidação;
15. rever alterações;
16. actualizar documentação;
17. actualizar o estado do projecto;
18. produzir relatório de conclusão;
19. sincronizar Git quando autorizado.

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

Responsabilidades:

- `/wsai` — entrada/orientação do fluxo;
- `/wsai-run` — orquestração autónoma do ciclo completo;
- `/wsai-audit` — fotografia do estado real, sem alteração funcional;
- `/wsai-plan` — planeamento sem implementação;
- `/wsai-implement` — implementação da unidade aprovada;
- `/wsai-test` — testes e correcção de falhas dentro do âmbito aprovado;
- `/wsai-validate` — gate de consolidação não destrutivo;
- `/wsai-doc` — documentação e estado persistente;
- `/wsai-git` — revisão, commit e sincronização.

`/wsai-run` não é uma arquitectura paralela: é apenas a composição destas responsabilidades. Se houver divergência entre um comando e o código real, corrigir primeiro o contrato do comando/documentação, sem alterar código funcional apenas para satisfazer documentação.

## Auditoria antes de expansão

Antes de criar um novo módulo, responsabilidade, registry, manager ou abstraction:

- localizar implementações equivalentes;
- verificar fronteiras arquitecturais;
- identificar consumidores existentes;
- verificar testes e documentação;
- classificar o gap como IMPLEMENTADO, PARCIAL, INTEGRAÇÃO NECESSÁRIA ou AUSENTE.

Preferir evolução aditiva e reversível. Não criar módulos vazios para necessidades futuras.

## Validação e qualidade

VALIDAR NÃO É IMPLEMENTAR.

`/wsai-validate` deve confirmar o estado sem alterar código funcional. Uma aprovação não pode basear-se apenas no número de testes: deve considerar comportamento observado, contratos, fronteiras, integração, recuperação, segurança e consistência entre código, testes e documentação.

Um teste que passa sem exercer o comportamento que pretende verificar é uma lacuna de qualidade e deve ser corrigido antes de usar esse teste como evidência de aprovação.

Ciclo formal:

```text
AUDIT
  ↓
PLAN
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
```

## Selecção de modelos OpenCode

Não fixar a arquitectura a um nome concreto de modelo.

Utilizar perfis de trabalho:

- FAST: tarefas simples e verificações rápidas;
- CODE: implementação e depuração;
- REASONING: arquitectura e problemas complexos;
- REVIEW: revisão independente;
- DOCUMENTATION: documentação técnica.

A escolha concreta deve respeitar os modelos efectivamente disponíveis na configuração OpenCode do utilizador.

## Autonomia controlada

O desenvolvimento pode continuar autonomamente entre unidades relacionadas, desde que:

- não exista falha de validação;
- não exista conflito arquitectural;
- não seja necessária uma alteração de requisitos fundamentais;
- o estado Git seja seguro;
- cada unidade produza informação suficiente para recuperação posterior;
- a próxima unidade esteja claramente definida e não introduza uma decisão arquitectural material não registada.

Quando uma unidade ou gate falhar, não avançar apenas para manter o fluxo. Classificar a falha e regressar ao ponto apropriado do ciclo.

## Critério de conclusão de uma base

Uma base só é concluída quando possui:

- implementação completa para o âmbito definido;
- testes adequados e significativos;
- validação executada;
- documentação actualizada;
- relatório de fase ou base;
- estado arquitectural actualizado;
- estado Git coerente e verificável.

## Relatório obrigatório

Cada conclusão relevante deve indicar:

1. o que foi implementado;
2. onde se enquadra na arquitectura;
3. para que serve;
4. módulos e dependências envolvidos;
5. testes executados;
6. problemas encontrados e sua prioridade;
7. resultado da validação;
8. estado actual da fase;
9. próximo passo recomendado.
