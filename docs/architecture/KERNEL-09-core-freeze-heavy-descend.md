# KERNEL-09 — CORE FREEZE (implementação pesada fora do núcleo)

- **Data:** 2026-09-09
- **Unidade:** KERNEL-09 (secção 12 de `CORE_KERNEL_TARGET.md`)
- **Estado:** CONCLUÍDA
- **Decisão aplicada:** descida completa da implementação pesada para
  `wsai2.infrastructure` (opção confirmada pelo utilizador no planeamento),
  fechando a decisão em aberto do KERNEL-08.
- **Ficheiros alterados:** 1 subsistema novo (`wsai2.infrastructure`, 8 ficheiros
  incluindo `__init__.py`), `resource/__init__.py`, `runtime_engine/__init__.py`
  (shells de re-export), `tests/architecture_contracts.py`,
  `tests/test_architecture_contract.py`, `tests/test_boundary_kernel.py`,
  `docs/infrastructure/BASE-44-*.md`, registos do projecto e este relatório.

## Objectivo

"Core freeze" = núcleo consolidado com a **implementação pesada fora do
núcleo**: `execution.runner`, `resource.governor`, `RuntimeManager`,
`Scheduler`, filas e monitor deixam de residir nos pacotes do kernel e passam
para infra-estrutura especializada, **por trás** dos contratos públicos
(critério de qualidade da sec. 11 do alvo: "a implementação pesada ocorre por
trás dos contratos públicos, sem residir no núcleo").

## Descida efectuada (`wsai2.infrastructure`)

```
resource/        ->  shells de re-export (superfície + versão intactas)
runtime_engine/  ->  (idem)
infrastructure/
    base_resource.py   (ex-resource/base.py:       tipos de governação)
    governor.py        (ex-resource/governor.py:   livro de alocações)
    base_runtime.py    (ex-runtime_engine/base.py: tipos/relatórios)
    manager.py         (ex-runtime_engine/manager.py: RuntimeManager)
    scheduler.py       (ex-runtime_engine/scheduler.py: Scheduler)
    queue.py           (ex-runtime_engine/queue.py: filas multicamadas)
    monitoring.py      (ex-runtime_engine/monitoring.py: métricas)
```

Moves com `git mv` (história preservada). `execution` e `security` **ficam**
no núcleo — descer o runner criaria o ciclo `execution ⇄ infra`.

## Fronteiras (recomposição — 26 arestas, como antes)

- `resource → infrastructure`; `runtime_engine → infrastructure` (sai
  `resource → {core, extension, hardware, runtime}` e
  `runtime_engine → {core, execution, resource, security, task}`).
- `infrastructure → {core, execution, extension, hardware, runtime, security,
  task}`.
- `FRONTEIRAS`/`FIREWALL` reescritos na fonte única
  (`tests/architecture_contracts.py`); `infrastructure` fora de
  `KERNEL_SUBSISTEMAS` (não é superfície de contrato: sem versão/`__all__`).
  A suíte de contrato verifica as 26 arestas reais do código.

## Guardas novos

- `test_implementacao_pesada_fora_do_nucleo` — `resource`/`runtime_engine`
  contêm apenas `__init__.py`; `wsai2.infrastructure` contém os 7 módulos da
  mecânica pesada.
- Excepção de contrato no teste de pastas placeholder: os shells de re-export
  são deliberados (não são pastas vazias).

## Sem alteração de comportamento

Todos os consumidores importam ao nível do pacote (KERNEL-05/06), por isso a
suíte completa permanece verde sem tocar nos ~30 ficheiros de teste do domínio.

## Validação

```text
py -3.12 -m pytest
tests=504  failures=0  errors=0  skipped=0
```

(504 = 503 + 1 guarda de descida.)

## Próximo passo

`/wsai-plan KERNEL-10` — Addon SDK / Projects foundation.