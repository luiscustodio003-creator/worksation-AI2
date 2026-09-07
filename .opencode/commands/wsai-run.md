# /wsai-run — ORQUESTRADOR AUTÓNOMO DO WORKSTATION AI 2

## Missão

Executar a próxima unidade lógica de desenvolvimento do WorkStation AI 2 de forma controlada, respeitando a arquitectura, a documentação, os testes e o estado do repositório.

## Entrada

Quando o utilizador executar:

```text
/wsai-run
```

não assumir que o projecto está vazio nem que a fase anterior foi concluída.

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

## FASE E — IMPLEMENTAÇÃO

Implementar de acordo com:

- `AGENTS.md`;
- constituição arquitectural;
- skill `wsai-development`;
- responsabilidade única;
- compatibilidade Windows/Linux quando aplicável.

O código deve possuir documentação técnica detalhada e comentários úteis em português de Portugal.

Não criar uma estrutura artificialmente complexa.

## FASE F — VALIDAÇÃO

Executar os testes aplicáveis.

Se a base de testes ainda não existir, criar primeiro a configuração mínima necessária e validar essa fundação.

Não declarar sucesso quando existirem falhas ignoradas.

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

## Regra de continuidade

Se a unidade actual estiver concluída e o ambiente continuar disponível, pode avançar para a próxima unidade apenas quando esta depender directamente da anterior e não introduzir uma nova decisão arquitectural de grande impacto.

Caso contrário, concluir, sincronizar e reportar.
