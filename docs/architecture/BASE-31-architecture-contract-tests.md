# WORKSTATION AI 2 — RELATÓRIO DA BASE: ARCHITECTURE CONTRACT TESTS

## O que foi feito

Foi implementada a unidade **Fase 8.7 — Testes de contrato arquitectural**
(hardening 11 do CORE_HARDENING_PLAN): um único ficheiro de testes,
`tests/test_architecture_contract.py` (10 testes), que transforma as
regras da CONSTITUTION e do AGENTS em **testes executáveis** verificados
contra a árvore real de `src/wsai2` e `docs/`. Não foi criado nem alterado
qualquer módulo de produção.

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine**, último passo da "ordem recomendada" do
  hardening 11 antes do **Gate — Core pronto para addons**.
- O código testa o próprio repositório (estático, sem recursos externos —
  ARTIGO 9 da Constituição) e funciona idêntico em Windows e Linux
  (apenas `pathlib`/`ast` da stdlib).
- É a materialização directa da Constituição ARTIGO 2 (dependências),
  ARTIGO 4 (sistemas operativos), ARTIGO 8 (crescimento controlado),
  ARTIGO 10 (documentação) e ARTIGO 13 (independência de modelos/
  fornecedores) e do AGENTS (fronteiras arquitecturais, isolamento de
  código de SO, documentação por módulo).

## Para que serve

- **Travar regressões de fronteira:** se um módulo vier a importar outro
  subsistema fora da lista autorizada, ou se for introduzido um ciclo de
  import em runtime, os testes falham no CI antes de qualquer execução.
- **Garantir isolamento de SO:** nenhum ficheiro fora de `wsai2.platform`
  pode referenciar `wsai2.platform.windows`/`linux`; a API pública da
  plataforma (`get_platform`) não expõe os adaptadores.
- **Garantir documentação:** todo o ficheiro de `src/wsai2` tem docstring
  do módulo e cada subsistema tem `docs/<nome>/BASE-*.md`.
- **Impedir antecipação:** subsistemas futuros (api, ui, knowledge —
  Fases 9–11) estão proibidos de existir como pastas placeholder, e
  nenhuma pasta pode viver só com `__init__.py` que não re-exporta.

## Ficheiros criados/alterados

- `tests/test_architecture_contract.py` — 10 testes de contrato
- `docs/architecture/BASE-31-architecture-contract-tests.md` — este relatório

Nenhum módulo de produção nem qualquer outro teste existente foi alterado.

## Dependências

- Apenas stdlib (`ast`, `pathlib`) e `pytest` (já na base de testes).
- Sem dependências de módulos de produção — o teste é auto-contido e
  determinístico.

## Regras executáveis e fundamento documental

| # | Teste | Regra |
|---|-------|-------|
| 1 | docstring em todos os fontes | Artigo 1 + Artigo 10 |
| 2 | todos os subsistemas têm BASE-*.md | Artigo 10 + AGENTS §3.9 |
| 3 | arestas de import autorizadas (`FRONTEIRAS`) | Artigo 2 + Artigo 13 |
| 4 | imports apontam para subsistemas reais | crescimento controlado |
| 5 | adaptadores de SO só na `platform` | Artigo 4 |
| 6 | `get_platform` é o ponto único de entrada | Artigo 4 |
| 7 | Windows/Linux não se importam entre si | Artigo 4 |
| 8 | sem ciclos de import em runtime | Artigo 2 (dependências) |
| 9 | api/ui/knowledge não antecipados | Artigo 8 (Fases 9–11) |
| 10 | nenhuma pasta placeholder | Artigo 8 |

A lista `FRONTEIRAS` (aresta autorizada por subsistema) espelha a
auditoria real da 8.7; cresce **apenas** com justificação documental.

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **364 testes aprovados** (10 novos desta unidade + 354 bases
anteriores). Regressão intacta — alteração 100% aditiva e sem tocar em
código de produção.

## Estado da fase

Fase 8 — Runtime Engine: concluídas **8.1 a 8.7** (a presente unidade
fecha a ordem recomendada do plano de hardening). Falta o **Gate — Core
pronto para addons**, que requer a decisão de Security/Policy (hardening
09) e Project Isolation (hardening 10) antes de activar addons de alto
impacto (código, ficheiros externos, GitHub, agentes, MCP).

## Riscos residuais

- `FRONTEIRAS` é uma fotografia estática verificada contra a auditoria;
  novas arestas legítimas (ex.: futuro addon -> resource) terão de ser
  adicionadas explicitamente — o que é o comportamento desejado (controlo
  de crescimento, Artigo 8).
- A detecção de ciclo ignora `TYPE_CHECKING` (aresta tipográfica não é
  aresta de runtime). Um mau uso futuro fora de `TYPE_CHECKING` seria
  detectado pelo teste 3 (fronteiras) e pelo teste 8 (ciclos).
- O parser AST cobre imports normais; mecanismos dinâmicos de import
  (importlib ad-hoc) não são analisados — adiados por não existirem na
  base.

## Próximo passo

**Decisão arquitectural material — Security / Policy (hardening 09) e
Project Isolation (hardening 10)** antes do Gate de addons: definir o
modelo `principal → project → capability → resource → action → policy →
decision` e a propagação/preservação de `project_id` nas fronteiras. São
responsabilidades ainda sem módulo próprio e com contrato novo na Fase 8 —
exigem auditoria e planeamento dedicados antes de qualquer implementação.