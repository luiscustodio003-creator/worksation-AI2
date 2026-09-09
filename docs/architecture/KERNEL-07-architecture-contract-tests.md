# KERNEL-07 — ARCHITECTURE CONTRACT TESTS

- **Data:** 2026-09-09
- **Unidade:** KERNEL-07 (secção 12 de `CORE_KERNEL_TARGET.md`)
- **Estado:** CONCLUÍDA
- **Ficheiros alterados:** `tests/architecture_contracts.py` (novo), `tests/test_architecture_contract.py`, `tests/test_boundary_kernel.py`, `tests/test_core_public.py`, `docs/project/PROJECT_STATE.md`, `docs/project/IMPLEMENTATION_LOG.md`, `docs/architecture/CORE_KERNEL_TARGET.md`, este relatório.

## Objectivo

Consolidar os contratos de fronteira já criados (KERNEL-03/04/05/06) numa
**fonte única de verdade** para os testes de arquitectura, eliminar a
duplicação de tabelas e fechar a cobertura: todos os subsistemas do kernel
com a sua superfície versionada verificada no mesmo gate.

## Duplicação eliminada

As tabelas de contrato estavam declaradas como literais em três ficheiros:

| Ficheiro | Antes (literais) | Depois (import — `tests/architecture_contracts.py`) |
| --- | --- | --- |
| `test_architecture_contract.py` | `FRONTEIRAS`, `SUBSISTEMAS_FUTUROS`, `FIREWALL`, `_ADAPTADORES_SO` | import |
| `test_boundary_kernel.py` | `SUPERFICIES_PUBLICAS`, `OBSERVABILIDADE_SUPERFICIE`, `GOVERNO_SUPERFICIE` | import |
| `test_core_public.py` | `SUPERFICIE` (core.public) | `CORE_PUBLIC_SUPERFICIE` import |

`tests/architecture_contracts.py` (módulo de dados, não é recolhido como
teste) concentra agora: `FRONTEIRAS` (26), `FIREWALL` (14),
`SUBSISTEMAS_FUTUROS`, `ADAPTADORES_SO`, `KERNEL_SUBSISTEMAS`,
`CORE_PUBLIC_SUPERFICIE`, `SUPERFICIES_PUBLICAS`,
`OBSERVABILIDADE_SUPERFICIE`, `GOVERNO_SUPERFICIE`, `MODULO_CONTRATO`,
`CONTRATO_CONSTANTES` e `CONTRACT_VERSIONES`.

## Novo guarda automatizado

`test_kernel_todas_as_superficies_publicas_versionadas` — para cada
subsistema do kernel (`core`, `execution`, `resource`, `runtime_engine`,
`security`): a constante de versão existe, é `major.minor`, é igual à
versão esperada registada (bump = alteração deliberada e simultânea) e —
para as fronteiras não-folha — não faz parte do `__all__`.

## Sem alteração de comportamento

Refactor de testes puro: nenhum ficheiro de `src` foi alterado; zero
arestas novas; `FIREWALL` e aciclicidade verificados tal como antes.

## Validação

```text
py -3.12 -m pytest
tests=502  failures=0  errors=0  skipped=0
```

(502 = 501 + 1 teste consolidado do kernel.)

## Próximo passo

`/wsai-plan KERNEL-08` — Migração incremental de imports (superfície
preservada; implementação pesada desce para infra-estrutura por trás dos
contratos públicos).