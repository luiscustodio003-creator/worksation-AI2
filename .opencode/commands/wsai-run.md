# /wsai-run — ORQUESTRADOR AUTÓNOMO DO WORKSTATION AI 2

## Missão

Executar a próxima unidade lógica de desenvolvimento do WorkStation AI 2 de forma controlada, respeitando a arquitectura, a documentação, os testes e o estado do repositório.

`/wsai-run` é um **orquestrador de execução**, não um comando de consulta. Depois de determinar a próxima unidade válida, deve executar o ciclo completo até concluir a unidade, atingir um bloqueio real ou encontrar uma decisão arquitectural que exija intervenção humana.

## Entrada

Quando o utilizador executar:

```text
/wsai-run
```

não assumir que o projecto está vazio nem que a fase anterior foi concluída.

## REGRA FUNDAMENTAL DE EXECUÇÃO AUTÓNOMA

Depois de determinar a próxima unidade lógica em `PROJECT_STATE.md`/`ROADMAP.md`, o agente **DEVE avançar automaticamente para o planeamento, implementação, validação, documentação e sincronização dessa unidade**.

**NÃO deve parar apenas porque conseguiu identificar ou apresentar a "PRÓXIMA UNIDADE".**

O texto "PRÓXIMA UNIDADE" é informação para o processo interno e/ou para o relatório final; não é um ponto de paragem.

O ciclo só pode terminar quando ocorrer uma destas condições:

1. a unidade foi concluída, validada, documentada e sincronizada;
2. existe uma falha técnica real que não pode ser resolvida autonomamente com segurança;
3. existe conflito/divergência Git que não pode ser resolvido com segurança;
4. é necessária uma decisão arquitectural nova e material que não esteja definida na documentação existente.

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

Se a estrutura mínima ainda não existir, inicializar apenas a unidade necessária para continuar a Fase 0.

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

Se existir conflito ou divergência que não possa ser resolvida com segurança, parar e reportar.

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

### Exemplo obrigatório de continuidade

Se `PROJECT_STATE.md` indicar:

```text
Fase 5 — Model Intelligence
Última unidade: registo, metadados e requisitos
Próxima unidade: compatibilidade
```

`/wsai-run` deve interpretar isso como:

```text
DETERMINADA → Fase 5 / Compatibilidade
↓
PLANEAR
↓
IMPLEMENTAR
↓
TESTAR
↓
DOCUMENTAR
↓
GIT
↓
ACTUALIZAR ESTADO
↓
RESULTADO
```

e **não** como:

```text
DETERMINADA → Fase 5 / Compatibilidade
↓
PARAR
```

## FASE D — PLANEAMENTO INTERNO

Antes de modificar código, identificar:

- objectivo da unidade;
- módulos afectados;
- novos ficheiros necessários;
- dependências;
- testes;
- documentação;
- riscos.

Manter o planeamento proporcional à dimensão da unidade.

O planeamento é interno e serve para iniciar a execução. Não deve ser tratado como resultado final nem como motivo para parar.

## FASE E — IMPLEMENTAÇÃO

Implementar de acordo com:

- `AGENTS.md`;
- constituição arquitectural;
- skill `wsai-development`;
- responsabilidade única;
- compatibilidade Windows/Linux quando aplicável.

O código deve possuir documentação técnica detalhada e comentários úteis em português de Portugal.

Não criar uma estrutura artificialmente complexa.

Se durante a implementação forem encontrados problemas menores e solucionáveis sem alterar a arquitectura, corrigi-los autonomamente e continuar.

## FASE F — VALIDAÇÃO

Executar os testes aplicáveis.

Se a base de testes ainda não existir, criar primeiro a configuração mínima necessária e validar essa fundação.

Não declarar sucesso quando existirem falhas ignoradas.

Se existirem falhas corrigíveis relacionadas com a unidade, **DEVE tentar corrigi-las e voltar a executar a validação** antes de terminar.

Só parar por falha quando a continuação segura deixar de ser possível.

## FASE G — DOCUMENTAÇÃO E ESTADO

Actualizar, conforme aplicável:

- documentação do módulo;
- `PROJECT_STATE.md`;
- `IMPLEMENTATION_LOG.md`;
- relatório específico da base concluída.

O relatório deve explicar:

- o que foi feito;
- onde se encaixa na arquitectura;
- para que serve;
- dependências;
- testes;
- estado da fase;
- próximo passo.

**`PROJECT_STATE.md` deve ser actualizado para reflectir a unidade realmente concluída antes do relatório final.**

## FASE H — GIT E SINCRONIZAÇÃO

Depois da validação:

1. inspeccionar `git diff`;
2. confirmar ficheiros modificados;
3. verificar se a alteração representa uma unidade coerente;
4. criar commit descritivo quando permitido;
5. efectuar push para o remoto quando as credenciais e o ambiente o permitirem;
6. verificar novamente o estado.

Nunca esconder uma falha de sincronização. Reportar claramente se o push não foi possível.

## FASE I — RESULTADO FINAL

Apresentar apenas progresso relevante durante a execução.

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

A secção `PRÓXIMA UNIDADE` deve ser calculada **depois** de actualizar `PROJECT_STATE.md`. Ela serve para informar qual será o próximo trabalho, não para interromper a unidade actual.

## REGRA DE CONTINUIDADE ENTRE UNIDADES

Depois de concluir, validar, documentar e sincronizar uma unidade, o agente deve avaliar se existe uma próxima unidade claramente definida e directamente dependente da anterior.

Se a próxima unidade for pequena, bem especificada e não introduzir uma decisão arquitectural de grande impacto, **pode continuar automaticamente no mesmo `/wsai-run`**.

Se a próxima unidade introduzir uma decisão arquitectural material, deve concluir a unidade actual, actualizar toda a documentação e parar com um relatório claro indicando a decisão necessária.

A regra de continuidade entre unidades **não substitui** a regra fundamental: a unidade já determinada no início desta execução deve ser executada; nunca deve ser apenas identificada e apresentada.
