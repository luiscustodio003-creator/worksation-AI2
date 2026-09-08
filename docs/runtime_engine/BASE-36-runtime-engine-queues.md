# BASE-36 — Filas multicamadas do Runtime Engine

## Estado

**IMPLEMENTADA — Fase 8 residual 3.** A validação integral da suíte deve ser executada no ambiente local/CI antes de declarar a baseline final.

## Objectivo

Fechar o último residual funcional da Fase 8: introduzir uma camada de filas por prioridade, com backlog e preempção de trabalho ainda pendente, sem substituir nem alterar destrutivamente o scheduler directo existente.

## Implementação

Foi criado `wsai2.runtime_engine.queue` com:

- `MultilayerExecutionQueue[T]` thread-safe;
- camada `ready` ordenada por `ExecutionPriority`;
- `backlog` para trabalho que não cabe na capacidade pronta;
- `max_ready` opcional;
- preempção apenas de itens pendentes: uma prioridade superior pode deslocar a menor prioridade pronta para o backlog;
- promoção automática do melhor item do backlog quando existe espaço;
- ordem estável por sequência de admissão dentro da mesma prioridade;
- `snapshot()`, `pending()` e `clear()` para observabilidade e controlo;
- rejeição explícita de capacidade inválida via `ValidationError`.

## Integração

`Scheduler.run` ganhou o kwarg aditivo:

```python
queue: MultilayerExecutionQueue[ExecutionPlan] | None = None
```

Sem `queue`, a via histórica permanece inalterada. Com `queue`, os planos são admitidos na fila e consumidos pela mesma pipeline de execução, preservando prioridades, políticas, monitorização, timeout, recovery, `step_runner` e concorrência já existentes.

A preempção é deliberadamente limitada a trabalho que ainda não começou. A fila não interrompe threads nem tenta cancelar execução em curso.

## Testes adicionados

`tests/test_runtime_engine_queue.py` cobre:

1. prioridade e ordem estável;
2. backlog e preempção com capacidade limitada;
3. não-preempção de trabalho já escolhido;
4. `pending()`;
5. `clear()`;
6. validação de capacidade;
7. regressão da via directa do scheduler;
8. integração scheduler → fila multicamada.

## Arquitectura

A alteração permanece dentro de `wsai2.runtime_engine` e reutiliza `ExecutionPriority` do Core. Não cria um segundo scheduler, não duplica `ExecutionPlan`, não altera Task Intelligence e não introduz dependências de API/UI/Knowledge.

## Critério de fecho

A unidade está implementada e documentada. O fecho formal da Fase 8 requer ainda:

```text
pytest completo → /wsai-validate foundation → corrigir GAPs se existirem →
validar novamente → actualizar PROJECT_STATE → commit final
```

A nova pipeline GitHub Actions (`.github/workflows/tests.yml`) foi adicionada para tornar a execução da suíte verificável no repositório.
