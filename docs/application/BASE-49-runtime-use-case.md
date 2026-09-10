# WORKSTATION AI 2 — BASE-49: APPLICATION — USE-CASE RUNTIME (APP-05)

## Responsabilidade

Resolver o use-case de estado de runtime (Ramo A): montar o
`RuntimeProfileResponse` (contrato APP-02) a partir de `wsai2.runtime`
(`discover_runtime`). O serviço tipa o estado momentâneo (Runtime State)
— separado da capacidade estrutural (Hardware Capability, secção 4 da
arquitectura) — sem lógica central de decisão.

## Âmbito (APP-05)

- `RuntimeProfileService` em `wsai2.application.runtime_uc`:
  - `resolve(RuntimeProfileRequest) -> RuntimeProfileResponse`;
  - fonte injectável `profile_source` (por omissão `discover_runtime`);
  - exposição na superfície de `wsai2.application` (23 símbolos).
- `RuntimeProfile` (carga de CPU/memória, processos, uptime e
  disponibilidade) reutilizado integralmente.

**Fora do âmbito:** hardware (APP-04), compatibilidade (APP-06) e
decisões de agendamento (APP-08/10).

## Dependências

- `application → runtime` (já autorizada); imports ao nível do pacote;
  nenhuma aresta nova.

## Interfaces

```python
class RuntimeProfileService:
    def __init__(self, profile_source=None): ...
    def resolve(self, request: RuntimeProfileRequest) -> RuntimeProfileResponse: ...
```

## Validação

```text
py -m pytest
tests=541  failures=0  errors=0  skipped=0   (537 + 4 novos APP-05)
```