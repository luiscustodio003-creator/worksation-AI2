# WORKSTATION AI 2 — BASE-50: APPLICATION — USE-CASE CAPABILITIES (APP-06)

## Responsabilidade

Resolver o use-case de capacidades (Ramo A): montar o `CapabilitiesResponse`
(contrato APP-02) a partir de `wsai2.capability` (`build_compatibility`),
honrando o filtro opcional `CapabilitiesRequest.domain` e preservando a
distinção capacidade vs estado (secção 4 da arquitectura).

## Âmbito (APP-06)

- **Extensão do domínio `capability` (decisão de 2026-09-10):** as
  definições de capacidade passaram a identificar o seu domínio —
  `CapabilityDefinition.domain: CapabilityDomain` (de `wsai2.hardware`,
  aresta `capability → hardware` já autorizada). O catálogo base classifica
  `accelerated_ml` como `GRAPHICS` e as restantes como `COMPUTE`. Foi
  adicionado o agrupamento `CompatibilityReport.by_domain(domain)` — a
  lógica de agrupamento permanece no módulo de domínio.
- `CapabilitiesService` em `wsai2.application.capabilities_uc`:
  - fontes injectáveis `registry_source` (por omissão
    `create_default_registry`), `hardware_source` (`discover_hardware`) e
    `runtime_source` (`discover_runtime`);
  - `resolve(CapabilitiesRequest) -> CapabilitiesResponse`; quando
    `request.domain` é definido, o relatório é restrito às entradas desse
    domínio via `by_domain` (serviço apenas compõe, sem lógica de
    avaliação);
  - exposição na superfície de `wsai2.application` (26 símbolos).

**Fora do âmbito:** modelos (APP-07), tarefas (APP-08) e qualquer nova
avaliação de requisitos.

## Dependências

- `application → capability, hardware, runtime` — já autorizadas; imports
  ao nível do pacote.

## Interfaces

```python
class CapabilitiesService:
    def __init__(self, registry_source=None, hardware_source=None,
                 runtime_source=None): ...
    def resolve(self, request: CapabilitiesRequest) -> CapabilitiesResponse: ...
```

## Decisões

1. A associação de domínio vive em `wsai2.capability` (definição), não na
   Application — a Application não interpreta requisitos.
2. O filtro por domínio não altera os perfis de hardware/runtime do
   relatório; restringe apenas as entradas (reutiliza `by_domain`).

## Validação

```text
py -m pytest
tests=548  failures=0  errors=0  skipped=0   (541 + 3 domínio + 5 APP-06)
```