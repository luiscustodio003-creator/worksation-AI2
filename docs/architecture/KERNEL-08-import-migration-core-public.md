# KERNEL-08 — Migração incremental de imports (via `core.public`)

- **Data:** 2026-09-09
- **Unidade:** KERNEL-08 (secção 12 de `CORE_KERNEL_TARGET.md`)
- **Estado:** CONCLUÍDA
- **Decisão aplicada:** **Opção A** do plano — migração de imports para a
  superfície `core.public` + regra de contrato. A descida física da
  implementação pesada (Opção B/C) fica registada como decisão em aberto
  para unidade própria, sem ser antecipada.
- **Ficheiros alterados:** 13 módulos de `src/wsai2`, `src/wsai2/core/public.py`
  (docstring), `tests/test_architecture_contract.py` (regra nova),
  `docs/project/PROJECT_STATE.md`, `docs/project/IMPLEMENTATION_LOG.md`,
  `docs/architecture/CORE_KERNEL_TARGET.md`, este relatório.

## Objectivo

`core.public` (KERNEL-03) era a superfície versionada do núcleo mas **não
tinha consumidores**: os subsistemas importavam `wsai2.core.errors` e
`wsai2.core.context` directamente (13 módulos). KERNEL-08 migra os
consumidores para o único ponto de entrada do core e fixa a regra com um
guarda automatizado.

## Migração efectuada (mesmos objectos, nova origem)

| Módulo | Antes | Depois |
| --- | --- | --- |
| `execution/base.py`, `extension/{versioning,registry,lifecycle}.py`, `knowledge/registry.py` | `from wsai2.core.errors import ValidationError` | `from wsai2.core.public import ValidationError` |
| `execution/runner.py` | `context` + `errors` (2 imports) | `public` (`ExecutionContext`, `TimeoutError`) |
| `runtime_engine/{base,scheduler,queue}.py` | `context`/`errors` | `public` |
| `runtime_engine/manager.py` | `context` + `errors` (5) | `public` (6 símbolos) |
| `resource/governor.py` | `from wsai2.core.errors import ResourceError` | `public` |
| `security/policy.py`, `security/isolation.py` | `errors` | `public` |

`core.public` importa apenas os módulos folha `core.errors`/`core.context`
(imports relativos; sem ciclos). Nenhuma aresta, fronteira ou comportamento
mudou — `FRONTEIRAS`/`FIREWALL` inalteradas.

## Regra de contrato nova

**Consumidores do core importam apenas de `wsai2.core.public`.** Guarda:
`test_consumidores_core_apenas_via_public` — scan AST de `src/wsai2` fora do
pacote `core`; falha em qualquer `wsai2.core.errors`/`wsai2.core.context`
absoluto.

## Validação

```text
py -3.12 -m pytest
tests=503  failures=0  errors=0  skipped=0
```

(503 = 502 + 1 regra nova.)

## Decisão em aberto (não antecipada)

A descida física da implementação pesada (governor/manager/scheduler/queue/
monitoring para camada de infra-estrutura; `execution` permanece no núcleo —
ciclo `execution ⇄ infra` se descer) exige decisão arquitectural material e
unidade própria, como registado no plano KERNEL-08.