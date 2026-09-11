# WSAI 2 — BASE-60: API-06 — ENDPOINT DE MODELOS (`GET /models`)

## Responsabilidade

Apresentar o use-case `ModelsService` (APP-07) por trás do transporte
contract-first do subsistema `wsai2.api`: o handler `models` transforma o
`ModelsResponse` da camada Application num `ApiResponse` com payload
serializável em JSON (veredictos de compatibilidade dos modelos contra o
hardware, o runtime e as capacidades do sistema), sem lógica de domínio e
sem I/O próprio.

## Âmbito (API-06)

- Handler `models` em `wsai2.api.models` (apresentador fino, sem estado,
  serviço injectável).
- Rota `GET /models` registada no adapter `StdLibHttpGateway`.
- `models` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON dos `ModelVerdict`: `summary`, `counts`
  (`available`/`restricted`/`unavailable`) e `verdicts` com `model_id`,
  `state`, `is_available`, `summary`, `checks` (verificação por
  requisito, com tuplas convertidas em listas) e `missing_capabilities`.

**Fora do âmbito (unidades seguintes):** tasks, knowledge,
execution/status e o integration gate (API-07..10).

## Decisões

1. **Apresentador fino, serviço injectável** — o handler delega a recolha
   no `ModelsService` (injectável para determinismo nos testes), seguindo
   o padrão de API-02..05.
2. **Fronteira `api → application`** — o handler importa apenas contratos
   de use-case (`wsai2.application`); não toca nos domínios directamente.
   A aresta `("api", "application")` já estava sancionada; nenhuma aresta
   nova foi criada.
3. **Contrato JSON estável** — enums por `.value`; `checks` com
   `name`/`required`/`available`/`satisfied`; quando o valor é uma tupla
   (ex.: `required_capabilities`) é convertido em lista; `counts` e
   `summary` derivados dos veredictos.
4. **Dimensões da avaliação preservadas** — o veredicto reflecte as três
   dimensões do Model Intelligence: capacidades requeridas, requisitos
   estruturais (Hardware Capability) e requisitos de runtime (Runtime
   State), sem lógica no apresentador.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
models(ApiRequest, service: ModelsService | None = None) -> ApiResponse
# GET /models -> 200 {"summary": "...", "counts": {"available": n, ...},
#                     "verdicts": [{"model_id": "...", "state": "...",
#                                   "is_available": bool, "summary": "...",
#                                   "checks": [{"name": "...", "required": ...,
#                                               "available": ..., "satisfied": bool}],
#                                   "missing_capabilities": [...]}]}
```

## Ficheiros

- Novo: `src/wsai2/api/models.py`.
- Novo: `tests/test_api_models.py` (6 testes).
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (superfície `api` += `models`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10).

## Validação

```text
py -3.12 -m pytest
tests=601  failures=0  errors=0  skipped=0
```

(595 bases + 6 novos de API-06.)