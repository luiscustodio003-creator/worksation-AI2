---
description: Orquestrar autonomamente uma unidade completa de desenvolvimento WSAI 2
---
# /wsai-run — ORQUESTRADOR AUTÓNOMO DO WORKSTATION AI 2

## Missão

Executar a próxima unidade lógica de desenvolvimento do WorkStation AI 2 de forma controlada, respeitando arquitectura, contratos, documentação, testes e estado do repositório.

`/wsai-run` é o orquestrador de execução. Não deve assumir que a estrutura física actual é a arquitectura definitiva.

## CONTRATO DE TRANSIÇÃO ARQUITECTURAL

Ler e respeitar obrigatoriamente:

`docs/architecture/COMMAND_EXECUTION_CONTRACT.md`

Durante a reestruturação do Core/Kernel, considerar o projecto em estado `TRANSITION` salvo indicação explícita em documentação persistente.

Antes de qualquer alteração estrutural, classificar a operação:

```text
CREATE | ADAPT | MOVE | SPLIT | MERGE | DEPRECATE | DELETE | FREEZE
```

Aplicar `BEFORE EXTEND`: procurar primeiro uma responsabilidade equivalente já existente. Preferir reutilização/adaptação/adapter a duplicação.

### Protecção de migração

Em `TRANSITION`:

- preservar comportamento já validado;
- mapear consumidores antes de mover ou eliminar;
- validar o destino antes de remover a origem;
- executar alterações estruturais em unidades pequenas;
- testar e validar cada unidade;
- manter rollback possível;
- não misturar alterações funcionais não relacionadas;
- respeitar o Dependency Firewall;
- não considerar a documentação futura como implementação existente.

## VISIBILIDADE OBRIGATÓRIA DA EXECUÇÃO

A autonomia não pode eliminar a observabilidade. No início e em mudanças relevantes, apresentar:

```text
╔══════════════════════════════════════════════════╗
║ WSAI 2 — PROGRESSO                               ║
╠══════════════════════════════════════════════════╣
║ Fase:      ...                                   ║
║ Unidade:   ...                                   ║
║ Etapa:     ...                                   ║
║ Progresso: ██████░░░░ ...%                       ║
║ Estado:    LEGACY | TRANSITION | TARGET | FROZEN║
║                                                  ║
║ ✓ concluído                                      ║
║ ● em execução                                    ║
║ ○ pendente                                       ║
║                                                  ║
║ Próximo: ...                                     ║
╚══════════════════════════════════════════════════╝
```

Usar `EM EXECUÇÃO` quando não existir base real para percentagem. Nunca inventar progresso.

## FAMÍLIA DE COMANDOS

```text
/wsai-audit
/wsai-plan
/wsai-implement
/wsai-test
/wsai-validate
/wsai-doc
/wsai-git
```

`/wsai-run` compõe estas responsabilidades. Não deve criar uma segunda versão das regras de cada comando.

## AUTORIDADE DE EXECUÇÃO

Uma unidade autorizada por `PROJECT_STATE.md`/`ROADMAP.md` pode avançar autonomamente quando for reversível, verificável e não introduzir decisão arquitectural material.

`READY TO IMPLEMENT`, `APPROVED` e `APPROVED WITH WARNINGS` não são pedidos de confirmação humana.

Só parar perante decisão arquitectural material, requisitos fundamentais alterados, risco significativo de perda/corrupção de dados, conflito Git inseguro, falha técnica sem solução segura ou violação do Dependency Firewall que exija decisão.

## FASE A — PRE-FLIGHT

Inspeccionar:

1. directório actual;
2. estrutura real;
3. `AGENTS.md`;
4. `docs/project/PROJECT_STATE.md`;
5. `docs/project/ROADMAP.md`;
6. arquitectura e contratos aplicáveis;
7. `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`;
8. configuração OpenCode;
9. estado Git;
10. testes existentes.

## FASE B — SINCRONIZAÇÃO

Verificar Git antes de alterar:

```text
git status
git branch --show-current
git remote -v
git fetch --all --prune
```

Nunca sobrescrever alterações locais/remotas sem compreender a divergência.

## FASE C — DETERMINAÇÃO DA UNIDADE

Basear a escolha em estado persistente, roadmap, dependências, testes e arquitectura real.

Antes de executar uma unidade estrutural, identificar explicitamente:

- responsabilidade actual;
- consumidores;
- dependências;
- contrato;
- destino;
- classificação da alteração;
- rollback.

Não seleccionar uma unidade que dependa de base inexistente.

## FASE D — PLANEAMENTO

Identificar objectivo, componentes existentes, ficheiros afectados, contratos, dependências, testes, documentação, riscos e estratégia de migração.

Se houver decisão arquitectural material nova, terminar em `BLOCKED`.

## FASE E — IMPLEMENTAÇÃO

Implementar de forma incremental, preservando comportamento validado.

Para `MOVE`, `SPLIT`, `MERGE` ou `DELETE`, exigir mapeamento de consumidores e validação antes da remoção da origem.

Não criar módulos paralelos quando a responsabilidade já existir.

## FASE F — TESTE E VALIDAÇÃO

Executar testes focados, integração e suíte completa quando a alteração for estrutural ou antes do fecho da unidade.

Corrigir autonomamente falhas seguras relacionadas com a unidade e repetir a validação.

Verificar especialmente, quando comandos/arquitectura são afectados:

- execução autónoma;
- continuidade;
- progresso visível;
- selecção da próxima unidade;
- estado persistente;
- Dependency Firewall;
- ausência de regressões.

## FASE G — DOCUMENTAÇÃO E ESTADO

Actualizar, conforme aplicável:

- documentação arquitectural;
- documentação dos módulos;
- `PROJECT_STATE.md`;
- `IMPLEMENTATION_LOG.md`;
- relatórios de validação.

Não marcar trabalho como concluído antes da evidência correspondente.

## FASE H — GIT

Inspeccionar diff, confirmar âmbito, validar testes/documentação, criar commit coerente e efectuar push quando permitido.

Nunca fazer reset destrutivo ou force push como mecanismo normal de recuperação.

## FASE I — RESULTADO

Produzir:

```text
╔══════════════════════════════════════════════════╗
║ WSAI 2 — RESULTADO DA UNIDADE                   ║
╚══════════════════════════════════════════════════╝

✓ Unidade: ...
✓ Arquitectura: ...
✓ Implementação: ...
✓ Testes: ...
✓ Validação: ...
✓ Documentação: ...
✓ Git: ...
✓ GitHub: ...

ESTADO DA ARQUITECTURA
...

PRÓXIMA UNIDADE
...
```

## CONTINUIDADE

Depois de concluir uma unidade, determinar a próxima a partir do estado actualizado. Continuar automaticamente se for pequena, directamente dependente, especificada e sem decisão arquitectural material.

Não avançar automaticamente para uma alteração estrutural maior apenas porque é a próxima no roadmap: primeiro executar o gate de planeamento correspondente.
