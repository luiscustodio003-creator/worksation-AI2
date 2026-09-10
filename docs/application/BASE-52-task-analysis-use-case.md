# WORKSTATION AI 2 — BASE-52: APPLICATION — USE-CASE TASK ANALYSIS (APP-08)

## Responsabilidade

Resolver o use-case de análise de tarefa (Ramo A): montar o
`TaskAnalysisResponse` (contrato APP-02) a partir de `wsai2.task`
(classificação, requisitos, selecção de capacidades e plano de execução) —
a Application compõe os factos produzidos pelo domínio, sem tomar decisões
de execução e sem conhecer fornecedores.

## Âmbito (APP-08)

- `TaskAnalysisService` em `wsai2.application.tasks_uc`:
  - fontes injectáveis `capability_registry_source`
    (`wsai2.capability.create_default_registry`), `hardware_source`
    (`discover_hardware`), `runtime_source` (`discover_runtime`) e
    `model_registry_source` (`wsai2.model.create_default_registry`);
  - `resolve(TaskAnalysisRequest) -> TaskAnalysisResponse` encadeando, por
    ordem, `classify_task` → `requirements_for` → `select_capabilities` →
    `build_execution_plan` (com `provider_health` por omissão — a aresta
    `provider` **não** pertence ao FIREWALL da Application);
  - exposição na superfície de `wsai2.application` (28 símbolos).
- Nenhuma alteração aos domínios `task`, `capability` ou `model` (REUSE).

**Fora do âmbito:** execução (APP-10), conhecimento (APP-09) e qualquer
contacto com fornecedores de modelos.

## Dependências

- `application → capability, hardware, model, runtime, task` — todas já
  autorizadas; imports ao nível do pacote.

## Interfaces

```python
class TaskAnalysisService:
    def __init__(self, capability_registry_source=None, hardware_source=None,
                 runtime_source=None, model_registry_source=None): ...
    def resolve(self, request: TaskAnalysisRequest) -> TaskAnalysisResponse: ...
```

## Validação

```text
py -m pytest
tests=558  failures=0  errors=0  skipped=0   (553 + 5 novos APP-08)
```