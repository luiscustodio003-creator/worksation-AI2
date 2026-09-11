# WSAI 2 — BASE-63: API-09 — ENDPOINTS DE EXECUÇÃO, ESTADO E CANCELAMENTO

## Responsabilidade

Apresentar os use-cases `ExecutionService`, `ExecutionStatusService` e
`CancellationService` (APP-10) por trás do transporte contract-first do
subsistema `wsai2.api`: três handlers que compõem o ciclo de vida de uma
execução sobre HTTP — submissão, consulta de estado e cancelamento —
transformando as respostas da camada Application em payloads serializáveis
em JSON. Cada handler é um apresentador fino, sem lógica de domínio e sem
I/O próprio, delegando nos serviços injectáveis para determinismo.

## Âmbito (API-09)

- `src/wsai2/api/executions.py` — módulo único com três handlers:
  - `execution_start` (`POST /executions`): submete uma tarefa para
    execução; recebe `task_id`, `kind`, `prompt`, `max_tokens`,
    `required_capabilities` e opções `priority`/`timeout_seconds`; devolve
    `task_id`, `plan` e `report`.
  - `execution_status` (`POST /executions/status`): consulta o estado de
    uma execução; recebe `execution_id`; devolve `execution_id`, `status`,
    `snapshot` e `report`.
  - `execution_cancel` (`POST /executions/cancel`): cancela uma execução;
    recebe `execution_id`; devolve `execution_id` e `cancelled`.
- Três rotas registadas no adapter `StdLibHttpGateway`.
- Três funções expostas na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON de `ExecutionPlan`, `ExecutionReport` (com
  `StepOutcome`), `ExecutionSnapshot` e `WsaiError` — duck typing puro,
  sem importar de `wsai2.infrastructure` (sem novas arestas arquitecturais).
- Validação de entrada: body JSON obrigatório (400), `kind` restrito ao
  enum de `TaskKind` (400), `execution_id` obrigatório (400).

**Sem novas arestas arquitecturais** — reutiliza `api → application`,
`api → task` e `api → core` (via `wsai2.core.public`). Os tipos de
relatório/estado (`ExecutionReport`, `ExecutionSnapshot`, `StepOutcome`)
são serializados por duck typing (padrão de API-02..06).

**Fora do âmbito:** API-10 — Integration Gate.

## Decisões

1. **POST para as três rotas** — o transporte stdlib remove a query string
   do path antes de rotear, impossibilitando `GET /executions/status?id=...`;
   POST com body JSON é consistente com os endpoints de entrada (API-07/08)
   e permite validação uniforme.
2. **Módulo único `executions.py`** — três handlers que partilham helpers
   de parsing/serialização; módulo coerente para o ciclo de vida da
   execução (submit/status/cancel), mais limpo que três ficheiros
   separados.
3. **Duck typing para serialização** — os tipos de relatório/estado vivem
   em `wsai2.infrastructure` (KERNEL-09); o `api` não pode importar de
   `infrastructure` (firewall). Aceder a atributos via duck typing mantém
   o padrão de API-02..06 e evita arestas novas.
4. **Fidelidade ao domínio APP-10** — sem gestor, o plano não é executável
   (report null); sem fonte de cancelamento, `cancelled=False`. O
   apresentador não inventa efeitos laterais.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → task` (tipos de entrada da tarefa, já existente da API-07).
- `api → core` (via `wsai2.core.public` apenas — regra KERNEL-08).
- Sem novas arestas (duck typing para `ExecutionReport`/`Snapshot`/`StepOutcome`).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
# POST /executions  body={"task_id", "kind", "prompt", "max_tokens",
#                         "required_capabilities", "priority?", "timeout_seconds?"}
# -> 200 {"task_id", "plan": {...} | null, "report": {...} | null}

# POST /executions/status  body={"execution_id"}
# -> 200 {"execution_id", "status", "snapshot": {...} | null, "report": {...} | null}

# POST /executions/cancel  body={"execution_id"}
# -> 200 {"execution_id", "cancelled": bool}
```

## Ficheiros

- Novo: `src/wsai2/api/executions.py`.
- Novo: `tests/test_api_execution.py` (15 testes).
- Novo: `docs/api/BASE-63-api-execution-endpoints.md`.
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (superfície `api` += 3 funções),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10),
  `docs/project/PROJECT_STATE.md`, `docs/project/ROADMAP.md`.

## Validação

```text
python -m pytest
tests=635  failures=0  errors=0  skipped=0
```

(620 bases + 15 novos de API-09.)