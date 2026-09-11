# WSAI 2 — BASE-57: API-03 — ENDPOINT DE HARDWARE (`GET /hardware`)

## Responsabilidade

Apresentar o use-case `HardwareProfileService` (APP-04) por trás do
transporte contract-first do subsistema `wsai2.api`: o handler `hardware`
transforma o `HardwareProfileResponse` da camada Application num
`ApiResponse` com payload serializável em JSON (perfil estrutural: cpu,
memória, gpus, armazenamento e capacidades derivadas), sem lógica de
domínio e sem I/O próprio.

## Âmbito (API-03)

- Handler `hardware` em `wsai2.api.hardware` (apresentador fino, sem
  estado, serviço injectável).
- Rota `GET /hardware` registada no adapter `StdLibHttpGateway`.
- `hardware` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON do `HardwareProfile`: `overall_level`, resumos
  textuais (`cpu_summary`/`memory_summary`/`gpu_summary`/`storage_summary`),
  `cpu`, `memory`, `gpus` (lista), `storage` (lista) e `capabilities`
  (lista de `{"domain", "score", "level", "details"}`).

**Fora do âmbito (unidades seguintes):** runtime, capabilities, models,
tasks, knowledge, execution/status e o integration gate (API-04..10).

## Decisões

1. **Apresentador fino, serviço injectável** — o handler delega a recolha
   no `HardwareProfileService` (injectável para determinismo nos testes),
   seguindo o padrão de API-02.
2. **Fronteira `api → application`** — o handler importa apenas contratos
   de use-case (`wsai2.application`); não toca nos domínios directamente.
   A aresta `("api", "application")` já estava sancionada; nenhuma aresta
   nova foi criada.
3. **Contrato JSON estável** — estrutura fixa de chaves para clientes da
   API; enums serializados por `.value`; tuplas convertidas em listas.
4. **REUSE** — o endpoint reaproveita o `HardwareProfileService` do Ramo A
   e a serialização mantém-se na API como responsabilidade de apresentação.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
hardware(ApiRequest, service: HardwareProfileService | None = None) -> ApiResponse
# GET /hardware -> 200 {"overall_level": "...", "cpu": {...}, "memory": {...},
#                       "gpus": [...], "storage": [...], "capabilities": [...]}
```

## Ficheiros

- Novo: `src/wsai2/api/hardware.py`.
- Novo: `tests/test_api_hardware.py` (6 testes).
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (superfície `api` += `hardware`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10).

## Validação

```text
py -3.12 -m pytest
tests=582  failures=0  errors=0  skipped=0
```

(576 bases + 6 novos de API-03.)