# WSAI 2 — BASE-56: API-02 — ENDPOINT DE SISTEMA (`GET /system`)

## Responsabilidade

Apresentar o use-case `SystemInfoService` (APP-03) por trás do transporte
contract-first do subsistema `wsai2.api`: o handler `system` transforma o
`SystemInfoResponse` da camada Application num `ApiResponse` com payload
serializável em JSON (`platform` + `uptime`), sem lógica de domínio e sem
I/O próprio.

## Âmbito (API-02)

- Handler `system` em `wsai2.api.system` (apresentador fino, sem estado).
- Rota `GET /system` registada no adapter `StdLibHttpGateway` (tabelas
  `_ROTA_METODOS` / `_HANDLERS`).
- `system` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON estável: plataforma (`os`/`name`/`release`/`version`/
  `machine`) e uptime (`boot_timestamp`/`uptime_seconds`/`uptime_hours`/
  `uptime_days`), com `null` quando o uptime é indisponível.

**Fora do âmbito (unidades seguintes):** hardware, runtime, capabilities,
models, tasks, knowledge, execution/status e o integration gate (API-03..10).

## Decisões

1. **Apresentador fino, serviço injectável** — o handler delega a recolha
   no `SystemInfoService` (que pode ser injectado para determinismo nos
   testes), seguindo o padrão injectável da Application (APP-03).
2. **Fronteira `api → application`** — o handler importa apenas contratos de
   use-case (`wsai2.application`); não toca nos domínios directamente. A
   aresta `("api", "application")` já estava sancionada (`FRONTEIRAS`/`FIREWALL`);
   nenhuma aresta nova foi criada.
3. **Contrato JSON estável** — a chave `uptime` está sempre presente
   (`null` quando indisponível), evitando formas de resposta oscilantes
   para clientes da API.
4. **REUSE** — o endpoint reaproveita o `SystemInfoService` do Ramo A; não
   foi criada responsabilidade duplicada na API.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
system(ApiRequest, service: SystemInfoService | None = None) -> ApiResponse
# GET /system -> 200 {"platform": {...}, "uptime": {...}|null}
```

## Ficheiros

- Novo: `src/wsai2/api/system.py`.
- Novo: `tests/test_api_system.py` (6 testes).
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (superfície `api` += `system`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10).

## Validação

```text
py -3.12 -m pytest
tests=576  failures=0  errors=0  skipped=0
```

(570 bases + 6 novos de API-02.)