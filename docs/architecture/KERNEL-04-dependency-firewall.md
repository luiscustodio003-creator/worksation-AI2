# KERNEL-04 — DEPENDENCY FIREWALL

- **Data:** 2026-09-09
- **Unidade:** KERNEL-04 (sequência do kernel, secção 12 de `CORE_KERNEL_TARGET.md`)
- **Estado:** CONCLUÍDA
- **Ficheiros alterados:** `tests/test_architecture_contract.py`, `docs/project/PROJECT_STATE.md`, `docs/project/IMPLEMENTATION_LOG.md`, `docs/architecture/CORE_KERNEL_TARGET.md`, este relatório

## Objectivo

Tornar o `FRONTEIRAS` (união das arestas autorizadas) num **firewall exacto por subsistema**: cada subsistema passa a declarar, de forma explícita e testada automaticamente, de que outros subsistemas pode depender. Qualquer aresta nova fora da declaração é detectada no gate — o critério-alvo *"os imports proibidos forem detectáveis automaticamente"* passa a estar verificado de forma granular.

## Fundamento

- `COMMAND_EXECUTION_CONTRACT.md` — regra de dependências da transição (Application → Core Public API; Addon → Core Public API; Core → nenhum Application/Addon; Addon → nenhum outro Addon).
- `CORE_KERNEL_TARGET.md`, secção 6 (regra de dependências) e 7 (public/internal).
- `KERNEL-02` — mapa real de dependências (consumidores por scan AST).
- Artigo 2 da Constituição (camadas folha, p.ex. `core`).

## Regra do firewall

1. **Application e Addons** consomem o núcleo apenas pela superfície pública sancionada (`wsai2.core.public`, KERNEL-03). Até ao KERNEL-08 não existem consumidores novos a forcado; os imports internos actuais a `wsai2.core.errors`/`wsai2.core.context` são **grandfathered** e migram incrementalmente no KERNEL-08.
2. **`core` é folha:** não acede a execution/resource/runtime_engine/security nem a Application/Addons. A única aresta tipográfica autorizada (`core -> extension`) permanece para anotações de tipos.
3. **Addons** não dependem directamente de outros Addons.
4. **Sem MOVE físico:** o firewall é declarativo e testável; não altera módulos existentes.

## Mapa exacto (firewall por subsistema)

Extraído do grafo real com a mesma semântica do `FRONTEIRAS` (imports `TYPE_CHECKING` incluídos). 26 arestas no total.

| Subsistema | Destinos autorizados |
| --- | --- |
| capability | hardware, runtime |
| core | extension (tipográfica) |
| execution | core, resource |
| extension | core, security |
| hardware | *(ninguém)* |
| knowledge | core |
| model | capability, hardware, runtime |
| platform | *(ninguém)* |
| provider | *(ninguém)* |
| resource | core, extension, hardware, runtime |
| runtime | *(ninguém)* |
| runtime_engine | core, execution, resource, security, task |
| security | core |
| task | capability, hardware, model, provider, runtime |

`wsai2.core.public` não acrescenta arestas (imports relativos intra-`core`), pelo que a tabela coincide com o grafo pré-KERNEL-03.

## Detecção automática

Novo teste no contrato arquitectural:

- `test_artigo2_13_firewall_por_subsistema` — para cada subsistema, o conjunto de destinos realmente importados tem de estar contido no `FIREWALL` declarado; as chaves do firewall têm de cobrir **todos** os subsistemas do código. Um import novo ilegal falha no gate com os destinos extra listados.

O `FRONTEIRAS` (união) permanece como invariante histórico; o `FIREWALL` é mais estrito por natureza (por subsistema), cobrindo também a detecção de arestas novas *dentro* da união.

## Validação

```text
py -3.12 -m pytest
tests=497  failures=0  errors=0  skipped=0
```

(497 = 496 anteriores + 1 teste novo de firewall; contratos/fronteiras/aciclicidade inalterados.)

## Próximo passo

`/wsai-plan KERNEL-05` — Resource / Execution boundary (superfície pública de execution/resource/runtime_engine/security quando consumida pelos subsistemas do kernel).