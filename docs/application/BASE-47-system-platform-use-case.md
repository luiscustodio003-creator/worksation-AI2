# WORKSTATION AI 2 — BASE-47: APPLICATION — USE-CASE SYSTEM / PLATFORM (APP-03)

## Responsabilidade

Resolver o primeiro use-case do Ramo A: montar o `SystemInfoResponse`
(contrato APP-02) a partir das superfícies públicas de `wsai2.platform`
(plataforma) e `wsai2.runtime` (uptime). O serviço pertence à camada
Application — orquestra *recolha e tipagem* de payloads de domínio, sem
lógica central de decisão (constituição, artigo 7).

## Âmbito (APP-03)

- `SystemInfoService` em `wsai2.application.system`:
  - `resolve(SystemInfoRequest) -> SystemInfoResponse`;
  - fontes injectáveis `provider` (adaptador de plataforma) e
    `uptime_source` (uptime actual) — determinismo em testes e isolamento
    de SO (artigo 4: o código específico de SO vive só nos adaptadores);
  - por omissão usa `get_platform()` (ponto único de entrada) e
    `discover_runtime().uptime`.
- `SystemInfoService` exposto na superfície de `wsai2.application` e
  sancionado em `SUPERFICIES_PUBLICAS["application"]` (21 símbolos).
- `wsai2.platform` já expunha `PlatformInfo` (exposição aditiva APP-02).

**Fora do âmbito:** filtros, autenticação, cache ou transporte (API-02+).

## Dependências

- `application → platform` e `application → runtime` (já autorizadas no
  firewall APP-02); imports ao nível do pacote; nenhuma aresta nova.
- Nenhuma biblioteca externa; `SystemInfoService` não faz I/O directo.

## Interfaces

```python
class SystemInfoService:
    def __init__(self, provider=None, uptime_source=None): ...
    def resolve(self, request: SystemInfoRequest) -> SystemInfoResponse: ...
```

## Decisões

1. **Serviço injectável, não global** — as fontes de plataforma/uptime são
   passadas no construtor (padrão dos portes injectáveis da API/Provider);
   o produtor do run escolhe os adaptadores, o serviço não os constrói.
2. **Reutilização integral** — nada de cópias de `PlatformInfo`/`SystemUptime`;
   a resposta tipa directamente os tipos de domínio (REUSE).
3. **Uptime vindo do Runtime Intelligence** — preserva a separação
   Hardware Capability vs Runtime State (secção 4 da arquitectura): o uptime
   é estado, recolhido por `discover_runtime`.

## Validação

```text
py -m pytest
tests=533  failures=0  errors=0  skipped=0   (528 + 5 novos APP-03)
```