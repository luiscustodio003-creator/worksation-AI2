# WORKSTATION AI 2 — BASE-51: APPLICATION — USE-CASE MODELS (APP-07)

## Responsabilidade

Resolver o use-case de avaliação de modelos (Ramo A): montar o
`ModelsResponse` (contrato APP-02) a partir de `wsai2.model`
(`evaluate_models`), honrando o filtro opcional por categoria
(`ModelsRequest.category`) — a Application compõe factos de domínio, sem
lógica de avaliação.

## Âmbito (APP-07)

- `ModelsService` em `wsai2.application.models_uc`:
  - fontes injectáveis `model_registry_source` (por omissão
    `wsai2.model.create_default_registry`), `capability_registry_source`
    (`wsai2.capability.create_default_registry`), `hardware_source`
    (`discover_hardware`) e `runtime_source` (`discover_runtime`);
  - `resolve(ModelsRequest) -> ModelsResponse`; quando `request.category`
    é definido, os veredictos são restritos aos modelos dessa categoria,
    mapeando `model_id → categoria` via as definições do registo
    (`category_for` — função do domínio);
  - exposição na superfície de `wsai2.application` (27 símbolos).
- Nenhuma alteração ao domínio `model`: `ModelDefinition.category` e
  `category_for` já existiam (REUSE).

**Fora do âmbito:** tarefas (APP-08), recomendações de exequibilidade
(fora do contrato APP-02) e qualquer selecção de modelo executor.

## Dependências

- `application → capability, hardware, model, runtime` — todas já
  autorizadas; imports ao nível do pacote.

## Interfaces

```python
class ModelsService:
    def __init__(self, model_registry_source=None, capability_registry_source=None,
                 hardware_source=None, runtime_source=None): ...
    def resolve(self, request: ModelsRequest) -> ModelsResponse: ...
```

## Validação

```text
py -m pytest
tests=553  failures=0  errors=0  skipped=0   (548 + 5 novos APP-07)
```