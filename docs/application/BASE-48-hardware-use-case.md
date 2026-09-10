# WORKSTATION AI 2 — BASE-48: APPLICATION — USE-CASE HARDWARE (APP-04)

## Responsabilidade

Resolver o use-case de perfil de hardware (Ramo A): montar o
`HardwareProfileResponse` (contrato APP-02) a partir de `wsai2.hardware`
(`discover_hardware`). O serviço tipa o perfil estrutural (Hardware
Capability) sem lógica central de decisão (constituição, artigo 7).

## Âmbito (APP-04)

- `HardwareProfileService` em `wsai2.application.hardware_uc`:
  - `resolve(HardwareProfileRequest) -> HardwareProfileResponse`;
  - fonte injectável `profile_source` (por omissão `discover_hardware`);
  - exposição na superfície de `wsai2.application` (22 símbolos).
- `HardwareProfile` (perfil estrutural + capacidades por domínio) é
  reutilizado integralmente — nenhuma cópia.

**Fora do âmbito:** runtime (APP-05), compatibilidade (APP-06) e
filtragem/apresentação.

## Dependências

- `application → hardware` (já autorizada); imports ao nível do pacote;
  nenhuma aresta nova.

## Interfaces

```python
class HardwareProfileService:
    def __init__(self, profile_source=None): ...
    def resolve(self, request: HardwareProfileRequest) -> HardwareProfileResponse: ...
```

## Validação

```text
py -m pytest
tests=537  failures=0  errors=0  skipped=0   (533 + 4 novos APP-04)
```