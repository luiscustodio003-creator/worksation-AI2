# WSAI 2 — BASE-59: API-05 — ENDPOINT DE CAPACIDADES (`GET /capabilities`)

## Responsabilidade

Apresentar o use-case `CapabilitiesService` (APP-06) por trás do
transporte contract-first do subsistema `wsai2.api`: o handler
`capabilities` transforma o `CapabilitiesResponse` da camada Application
num `ApiResponse` com payload serializável em JSON (catálogo de
capacidades avaliadas contra o hardware e o runtime actuais), sem lógica
de domínio e sem I/O próprio.

## Âmbito (API-05)

- Handler `capabilities` em `wsai2.api.capabilities` (apresentador fino,
  sem estado, serviço injectável).
- Rota `GET /capabilities` registada no adapter `StdLibHttpGateway`.
- `capabilities` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON do `CompatibilityReport`: `summary`, `counts`
  (`available`/`restricted`/`unavailable`) e `entries` com `id`, `name`,
  `description`, `domain`, `state`, `is_available`, `justification`,
  `requirements` e `checks` (verificação por requisito).

**Fora do âmbito (unidades seguintes):** models, tasks, knowledge,
execution/status e o integration gate (API-06..10).

## Decisões

1. **Apresentador fino, serviço injectável** — o handler delega a recolha
   no `CapabilitiesService` (injectável para determinismo nos testes),
   seguindo o padrão de API-02..04.
2. **Fronteira `api → application`** — o handler importa apenas contratos
   de use-case (`wsai2.application`); não toca nos domínios directamente
   (o elemento do relatório é resolvido transitivamente pela coerência do
   contrato). A aresta `("api", "application")` já estava sancionada;
   nenhuma aresta nova foi criada.
3. **Contrato JSON estável** — enums por `.value`; `checks` como lista de
   objectos com `name`/`required`/`available`/`satisfied`; `summary` e
   `counts` derivados do relatório (o catálogo de capacidades disponíveis
   do roadmap da Fase 4).
4. **Distinção estrutura/runtime preservada** — o estado de cada entrada
   reflecte a separação secção 4: requisitos estruturais falhados → um
   `unavailable`, requisitos de runtime falhados → `restricted`.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
capabilities(ApiRequest, service: CapabilitiesService | None = None) -> ApiResponse
# GET /capabilities -> 200 {"summary": "...", "counts": {"available": n, ...},
#                           "entries": [{"id": "...", "name": "...", "domain": "...",
#                                        "state": "...", "is_available": bool,
#                                        "justification": "...",
#                                        "requirements": {...}, "checks": [...]}]}
```

## Ficheiros

- Novo: `src/wsai2/api/capabilities.py`.
- Novo: `tests/test_api_capabilities.py` (6 testes).
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (superfície `api` += `capabilities`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10).

## Validação

```text
py -3.12 -m pytest
tests=595  failures=0  errors=0  skipped=0
```

(589 bases + 6 novos de API-05.)