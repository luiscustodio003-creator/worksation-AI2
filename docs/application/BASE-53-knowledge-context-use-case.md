# WORKSTATION AI 2 — BASE-53: APPLICATION — USE-CASE KNOWLEDGE CONTEXT (APP-09)

## Responsabilidade

Resolver o use-case de contexto de conhecimento (Ramo A): montar o
`KnowledgeContextResponse` (contrato APP-02) a partir de `wsai2.knowledge`
(indexação, pesquisa com limite e filtro opcional por `KnowledgeKind` e
construção de contexto) — a Application não decide a localização do
armazenamento nem a política semântica.

## Âmbito (APP-09)

- `KnowledgeContextService` em `wsai2.application.knowledge_uc`:
  - fonte injectável `registry_source` (por omissão
    `wsai2.knowledge.KnowledgeRegistry`, registo vazio — o carregamento
    do armazenamento/path é decisão do caller/API, não da Application);
  - `resolve(KnowledgeContextRequest) -> KnowledgeContextResponse`:
    indexa o registo (`KnowledgeIndex().build`), pesquisa
    (`KnowledgeIndex().search`, respeitando `limit`), filtra por
    `request.kind` quando definido e constrói o contexto
    (`ContextBuilder().build(..., top=request.limit)`);
  - exposição na superfície de `wsai2.application` (29 símbolos).
- Nenhuma alteração ao domínio `knowledge` (REUSE).

**Fora do âmbito:** execução (APP-10), semântica avançada (Ramo D) e
qualquer I/O de armazenamento decidido aqui.

## Dependências

- `application → knowledge` — já autorizada; imports ao nível do pacote.

## Interfaces

```python
class KnowledgeContextService:
    def __init__(self, registry_source=None): ...
    def resolve(self, request: KnowledgeContextRequest) -> KnowledgeContextResponse: ...
```

## Validação

```text
py -m pytest
tests=562  failures=0  errors=0  skipped=0   (558 + 4 novos APP-09)
```