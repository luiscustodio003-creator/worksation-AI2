# WSAI DEVELOPMENT SKILL

## Objectivo

Esta skill governa o desenvolvimento incremental do WorkStation AI 2.

Não substitui a arquitectura do produto. A sua função é garantir que o trabalho de desenvolvimento permanece coerente, verificável e sincronizado.

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
9. seleccionar uma estratégia e o modelo OpenCode adequado à complexidade;
10. implementar apenas a unidade de trabalho aprovada;
11. criar ou actualizar testes;
12. executar validação;
13. rever alterações;
14. actualizar documentação;
15. actualizar o estado do projecto;
16. produzir relatório de conclusão.

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
- cada unidade produza informação suficiente para recuperação posterior.

## Critério de conclusão de uma base

Uma base só é concluída quando possui:

- implementação completa para o âmbito definido;
- testes adequados;
- validação executada;
- documentação actualizada;
- relatório de fase ou base;
- estado arquitectural actualizado.

## Relatório obrigatório

Cada conclusão relevante deve indicar:

1. o que foi implementado;
2. onde se enquadra na arquitectura;
3. para que serve;
4. módulos e dependências envolvidos;
5. testes executados;
6. problemas encontrados;
7. estado actual da fase;
8. próximo passo recomendado.
