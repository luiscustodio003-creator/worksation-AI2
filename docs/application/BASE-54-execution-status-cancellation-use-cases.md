# WORKSTATION AI 2 — BASE-54: APPLICATION — USE-CASES EXECUTION/STATUS/CANCELLATION (APP-10)

## Responsabilidade

Resolver os use-cases de execução, estado e cancelamento (Ramo A):
montar `ExecutionResponse`, `ExecutionStatusResponse` e
`CancellationResponse` (contrato APP-02) a partir de `wsai2.runtime_engine`
— a Application compõe a execução observada, sem implementar o motor nem
conhecer fornecedores.

## Âmbito (APP-10)

- `ExecutionService` em `wsai2.application.execution_uc`: fontes
  injectáveis `manager_source` (por omissão `RuntimeManager`), `monitor`
  (opcional, partido com consumidores) e `analysis` (por omissão
  `TaskAnalysisService`, REUSE de APP-08). `resolve` executa o plano quando
  executável; caso contrário devolve plano sem relatório.
- `ExecutionStatusService`: fonte `monitor_source` (por omissão
  `ExecutionMonitor`); `resolve` devolve relatório/estado quando concluída,
  fotografia quando em curso, ou nada.
- `CancellationService`: fonte `cancel_source: Callable[[str], bool]`
  injectável; **por omissão devolve `cancelled=False`** — o
  `runtime_engine` actual não expõe cancelamento por identificador (Kernel
  congelado), o efeito é delegado à fonte no API.
- Superfície de `wsai2.application` com 30 símbolos.

**Fora do âmbito:** motor de execução (Kernel), cancelamento no runtime e
qualquer decisão sobre fornecedores.

## Dependências

- `application → runtime_engine, task` — já autorizadas; imports ao nível
  do pacote.

## Interfaces

```python
class ExecutionService:
    def __init__(self, manager_source=None, monitor=None, analysis=None): ...
    def resolve(request: ExecutionRequest) -> ExecutionResponse: ...

class ExecutionStatusService:
    def __init__(self, monitor_source=None): ...
    def resolve(request: ExecutionStatusRequest) -> ExecutionStatusResponse: ...

class CancellationService:
    def __init__(self, cancel_source=None): ...
    def resolve(request: CancellationRequest) -> CancellationResponse: ...
```

## Validação

```text
py -m pytest
tests=570  failures=0  errors=0  skipped=0   (562 + 8 novos APP-10)
```