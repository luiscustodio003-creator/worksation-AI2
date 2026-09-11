# WSAI 2 — BASE-62: API-08 — ENDPOINT DE CONHECIMENTO (`POST /knowledge`)

## Responsabilidade

Apresentar o use-case `KnowledgeContextService` (APP-09) por trás do
transporte contract-first do subsistema `wsai2.api`: o handler `knowledge`
transforma o `KnowledgeContextResponse` da camada Application num
`ApiResponse` com payload serializável em JSON (correspondências e pacote de
contexto), sem lógica de domínio e sem I/O próprio. Segue o mesmo padrão de
entrada introduzido em API-07 (`POST /tasks`): corpo JSON descrevendo a
consulta, ligado ao contrato `KnowledgeContextRequest`.

## Âmbito (API-08)

- Handler `knowledge` em `wsai2.api.knowledge` (apresentador fino, sem
  estado, serviço injectável).
- Rota `POST /knowledge` registada no adapter `StdLibHttpGateway`.
- `knowledge` exposto na superfície pública `wsai2.api` (`__all__`).
- Serialização JSON do `KnowledgeContextResponse`: `query` (espelhada),
  `matches` (lista de registos `KnowledgeRecord` com `id`, `title`,
  `content`, `kind`, `metadata`/`source`/`language`/`author`/`tags`/`extras`
  e `created_at`) e `context` (`query`, `entries`/`record_id`/`title`/
  `snippet`/`source`/`tags` e `text` gerado por `KnowledgeContext.text()`;
  `null` quando não disponível).
- Entrada: `query` obrigatória e não vazia (400), `limit` positivo (400),
  `kind` opcional restrito ao enum de `KnowledgeKind` (`document`,
  `extract`, `note`) — valor desconhecido devolve 400.
- Nova aresta arquitectural **`api → knowledge`** justificada: o handler
  importa o enum `KnowledgeKind` de `wsai2.knowledge` para construir o
  `KnowledgeContextRequest` — a Application (Ramo A, `COMPLETE / FROZEN`)
  não re-exporta tipos de domínio; a arquitectura 3.10 autoriza arestas de
  recursos de domínio específicas e justificadas por unidade (mesma
  justificação de `api → task` na API-07).

**Fora do âmbito (unidades seguintes):** execution/status (API-09) e o
integration gate (API-10).

## Decisões

1. **`POST /knowledge` (não GET)** — como em API-07, o use-case exige uma
   entrada (a consulta); POST/corpo JSON são a semântica correcta.
2. **Apresentador fino, serviço injectável** — o handler delega no
   `KnowledgeContextService` (injectável para determinismo), seguindo o
   padrão de API-02..07.
3. **Fronteira `api → application | knowledge`** — o handler importa os
   contratos de use-case de `wsai2.application` e apenas o enum
   `KnowledgeKind` de `wsai2.knowledge`. A aresta `("api", "knowledge")`
   foi adicionada a `FRONTEIRAS` e ao `FIREWALL` de `api` em
   `tests/architecture_contracts.py` e justificada nesta base.
4. **Fidelidade ao domínio APP-09** — o handler não inventa correspondências
   nem contexto; serializa apenas o `KnowledgeContextResponse` devolvido pelo
   serviço (incluindo a representação textual determinista `context.text()`).
5. **Contrato JSON estável** — enums por `.value`; tuplas em listas; erro
   400 com `error` descritivo em PT para entradas inválidas. Sem limite de
   `limit` imposto pelo apresentador — o contrato de use-case valida
   positividade.

## Dependências

- `api → application` (contratos de use-case, ao nível do pacote).
- `api → knowledge` (nova aresta justificada — enum `KnowledgeKind`).
- `api → core` (apenas `wsai2.core.public`, regra KERNEL-08 — imutável).
- Nenhuma biblioteca externa nova (continua stdlib).

## Interfaces

```python
knowledge(ApiRequest, service: KnowledgeContextService | None = None) -> ApiResponse
# POST /knowledge  body={"query": "...", "limit": N, "kind": "document|extract|note"}
# -> 200 {"query": "...",
#          "matches": [{"id": "...", "title": "...", "content": "...",
#                       "kind": "...", "metadata": {"source": "...",
#                       "language": "...", "author": "...", "tags": [...],
#                       "extras": {...}}, "created_at": "..."}],
#          "context": {"query": "...", "entries": [{"record_id": "...",
#                       "title": "...", "snippet": "...", "source": "...",
#                       "tags": [...]}], "text": "..."} | null}
# -> 400 {"error": "..."}   body inválido / kind inválido / consulta vazia / limit inválido
# -> 405 {"error": "metodo nao suportado nesta rota"}   método != POST
```

## Ficheiros

- Novo: `src/wsai2/api/knowledge.py`.
- Novo: `tests/test_api_knowledge.py` (10 testes).
- Novo: `docs/api/BASE-62-api-knowledge-endpoint.md`.
- Modificado: `src/wsai2/api/transport_stdlib.py`, `src/wsai2/api/__init__.py`,
  `tests/architecture_contracts.py` (aresta `api→knowledge`, superfície `api` += `knowledge`),
  `docs/architecture/ARCHITECTURE.md` (secção 3.10),
  `docs/project/PROJECT_STATE.md`, `docs/project/ROADMAP.md`.

## Validação

```text
python -m pytest
tests=620  failures=0  errors=0  skipped=0
```

(610 bases + 10 novos de API-08.)