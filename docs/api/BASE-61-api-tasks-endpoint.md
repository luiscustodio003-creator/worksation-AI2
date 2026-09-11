# WSAI 2 — BASE-61: API-07 — ENDPOINT DE TAREFAS (`POST /tasks`)

## Responsabilidade

Apresentar o use-case `TaskAnalysisService` (APP-08) por trás do transporte
contract-first do subsistema `wsai2.api`: o handler `tasks` transforma o
`TaskAnalysisResponse` da camada Application num `ApiResponse` com payload
serializável em JSON (classificação, requisitos, selecção de capacidades e
plano de execução), sem lógica de domínio e sem I/O próprio. É o primeiro
endpoint da API que aceita **entrada** (corpo JSON descrevendo a tarefa) —
liga o parsing do pedido ao contrato `TaskAnalysisRequest`.

## Âmbito (API-07)

- Handler `tasks` em `wsai2.api.tasks` (apresentador fino, sem estado,
  serviço injectável).
- Rota `POST /tasks` registada no adapter `StdLibHttpGateway`.
- `tasks` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON do `TaskAnalysisResponse`: `task_id`, `classification`
  (`task_id`, `kind`, `category`), `requirements` (`task_id`, `category`,
  `required_capabilities`, `max_tokens`), `selection` (`task_id`, `required`,
  `available`, `missing`, `is_viable`) e `plan` (`task_id`, `category`,
  `feasible`, `model_id`, `provider_id`, `reasons`, `steps`,
  `is_executable`); campos opcionais como `selection`/`plan` são `null`
  quando indisponíveis.
- Validação de entrada: corpo JSON obrigatório (400), `kind` restrito ao
  enum de `TaskKind` (400), `Task` inválida devolve 400.
- Nova aresta arquitectural **`api → task`** justificada: o handler monta a
  `Task` (tipo de entrada do use-case APP-08) a partir do corpo JSON — a
  Application (Ramo A, `COMPLETE / FROZEN`) não re-exporta tipos de domínio;
  a arquitectura 3.10 autoriza arestas de recursos de domínio específicas e
  justificadas por unidade.

**Fora do âmbito (unidades seguintes):** knowledge (API-08),
execution/status (API-09) e o integration gate (API-10).

## Decisões

1. **`POST /tasks` (não GET)** — ao contrário dos endpoints de leitura
   (API-02..06), a análise de tarefa exige uma entrada (a descrição da
   tarefa); o verbo POST e o corpo JSON são a semântica correcta para esta
   operação.
2. **Apresentador fino, serviço injectável** — o handler delega a análise
   no `TaskAnalysisService` (injectável para determinismo), seguindo o
   padrão de API-02..06. O parsing do pedido é a única responsabilidade
   nova, limitada à validação de entrada.
3. **Fronteira `api → application | task`** — o handler importa os
   contratos de use-case de `wsai2.application` e apenas os tipos
   necessários à montagem da tarefa (`Task`, `TaskKind`) de `wsai2.task`.
   A aresta `("api", "task")` foi adicionada a `FRONTEIRAS` e ao `FIREWALL`
   de `api` em `tests/architecture_contracts.py` e justificada nesta base.
4. **Fidelidade ao domínio APP-08** — sem `provider_health` injectado, o
   plano devolve `model_id` recomendado e `provider_id` `null`, com
   `feasible`/`is_executable` reflectindo a realidade (nenhum fornecedor
   saudável conhecido). O apresentador não inventa fornecedores.
5. **Contrato JSON estável** — enums por `.value`; tuplas convertidas em
   listas; erro 400 com `error` descritivo em PT para entradas inválidas.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → task` (nova aresta justificada — tipos de entrada da tarefa).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
tasks(ApiRequest, service: TaskAnalysisService | None = None) -> ApiResponse
# POST /tasks  body={"task_id": "...", "kind": "chat|completion|embedding",
#                    "prompt": "...", "max_tokens": N,
#                    "required_capabilities": [...]}
# -> 200 {"task_id": "...", "classification": {"task_id": "...", "kind": "...",
#            "category": "..."},
#          "requirements": {"task_id": "...", "category": "..." ,
#            "required_capabilities": [...], "max_tokens": N},
#          "selection": {"task_id": "...", "required": [...], "available": [...],
#            "missing": [...], "is_viable": bool} | null,
#          "plan": {"task_id": "...", "category": "...", "feasible": bool,
#            "model_id": str|null, "provider_id": str|null, "reasons": [...],
#            "steps": [...], "is_executable": bool} | null}
# -> 400 {"error": "..."}   body inválido / kind inválido / tarefa inválida
# -> 405 {"error": "metodo nao suportado nesta rota"}   método != POST
```

## Ficheiros

- Novo: `src/wsai2/api/tasks.py`.
- Novo: `tests/test_api_tasks.py` (9 testes).
- Novo: `docs/api/BASE-61-api-tasks-endpoint.md`.
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (aresta `api→task`, superfície `api` += `tasks`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10),
  `docs/project/PROJECT_STATE.md`, `docs/project/ROADMAP.md`.

## Validação

```text
python -m pytest
tests=610  failures=0  errors=0  skipped=0
```

(601 bases + 9 novos de API-07.)