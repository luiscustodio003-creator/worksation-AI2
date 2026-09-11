# WSAI 2 — BASE-58: API-04 — ENDPOINT DE RUNTIME (`GET /runtime`)

## Responsabilidade

Apresentar o use-case `RuntimeProfileService` (APP-05) por trás do
transporte contract-first do subsistema `wsai2.api`: o handler `runtime`
transforma o `RuntimeProfileResponse` da camada Application num
`ApiResponse` com payload serializável em JSON (estado momentâneo — CPU,
memória, processos, uptime e disponibilidade efectiva), sem lógica de
domínio e sem I/O próprio.

## Âmbito (API-04)

- Handler `runtime` em `wsai2.api.runtime` (apresentador fino, sem
  estado, serviço injectável).
- Rota `GET /runtime` registada no adapter `StdLibHttpGateway`.
- `runtime` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON do `RuntimeProfile`: `overall_status`, resumos
  textuais (`cpu_summary`/`memory_summary`/`uptime_summary`/
  `availability_summary`), `cpu`, `memory`, `processes` (lista),
  `uptime` (ou `null`), `availability` (lista) e `top_process`.

**Fora do âmbito (unidades seguintes):** capabilities, models, tasks,
knowledge, execution/status e o integration gate (API-05..10).

## Decisões

1. **Apresentador fino, serviço injectável** — o handler delega a recolha
   no `RuntimeProfileService` (injectável para determinismo nos testes),
   seguindo o padrão de API-02/API-03.
2. **Fronteira `api → application`** — o handler importa apenas contratos
   de use-case (`wsai2.application`); não toca nos domínios directamente.
   A aresta `("api", "application")` já estava sancionada; nenhuma aresta
   nova foi criada.
3. **Contrato JSON estável** — enums por `.value`, tuplas em listas;
   `uptime` e `top_process` sempre presentes (`null` quando indisponíveis).
4. **Este endpoint distingue Runtime State de Hardware Capability** — o
   estado momentâneo é apresentado no `/runtime` (API-04), o perfil
   estrutural no `/hardware` (API-03); preservando a separação da
   arquitectura (secção 4).

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
runtime(ApiRequest, service: RuntimeProfileService | None = None) -> ApiResponse
# GET /runtime -> 200 {"overall_status": "...", "cpu": {...}, "memory": {...},
#                       "processes": [...], "uptime": {...}|null,
#                       "availability": [...], "top_process": {...}|null}
```

## Ficheiros

- Novo: `src/wsai2/api/runtime.py`.
- Novo: `tests/test_api_runtime.py` (7 testes).
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (superfície `api` += `runtime`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10).

## Validação

```text
py -3.12 -m pytest
tests=589  failures=0  errors=0  skipped=0
```

(582 bases + 7 novos de API-04.)