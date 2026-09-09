# WSAI 2 — FASE 9 VALIDATION REPORT

**Data:** 2026-09-09
**Commit:** d35874c
**Branch:** main
**Modo:** `/wsai-validate fase9`
**Alvo:** Knowledge Engine — subsistema 3.9 (âmbito lexical 9.1–9.7)

## 1. RESULTADO GLOBAL

**🟢 APPROVED**

O Knowledge Engine encontra-se implementado, testado, documentado e
alinhado entre código, testes e documentação, no seu **âmbito lexical**.
Não existem bloqueadores P0/P1/P2. O fecho declara a Fase 9 (âmbito
lexical) formalmente concluída; o enriquecimento semântico (embeddings)
é a decisão material terminal, registada no estado, que continua em
aberto por natureza (requer modelo/fornecedor e integração Provider).

## 2. INVENTÁRIO

Estado real da árvore (fonte primária: código + testes; documentação como
declaração de estado):

| Unidade | Componente (`wsai2.knowledge`) | Estado |
|---|---|---|
| 9.1 | Knowledge Contract (`base.py`) | IMPLEMENTADO |
| 9.2 | Knowledge Registry (`registry.py`) | IMPLEMENTADO |
| 9.3 | Metadata Extraction (`metadata.py`) | IMPLEMENTADO |
| 9.4 | In-Memory Index (`index.py`) | IMPLEMENTADO |
| 9.5 | SQLite Persistence (`storage.py`) | IMPLEMENTADO |
| 9.6 | Context Builder (`context.py`) | IMPLEMENTADO |
| 9.7 | File Ingestion (`ingest.py`) | IMPLEMENTADO |
| — | Enriquecimento semântico (embeddings) | AUSENTE (fora do âmbito lexical; decisão material terminal) |
| Fase 10 — API | `wsai2.api` | AUSENTE (fase futura) |
| Fase 11 — UI | `wsai2.ui` | AUSENTE (fase futura) |

## 3. ARQUITECTURA

- Subsistema 3.9 **autorizado**; `SUBSISTEMAS_FUTUROS = ("api", "ui")`.
- `FRONTEIRAS` com **22 arestas autorizadas** (nova: `knowledge→core`,
  justificada no BASE-38); circuito lexical fechado:
  **ficheiro → contrato → registo → metadados → índice → persistência →
  contexto**.
- Dependências apenas stdlib (`sqlite3`, `json`, `pathlib`, `re`,
  `collections`, `dataclasses`, `contextlib`) + `core.errors` — sem
  Runtime/Provider/Model acoplados ao núcleo lexical.
- `tokenize()` partilhado (normalização única entre extracção, índice e
  consulta); determinismo garantido por ordenações explícitas.
- Decisões consultadas e documentadas: **9.4 memória pura** (BASE-40) e
  **9.5 SQLite local** (BASE-41).

## 4. CÓDIGO E CONTRATOS

- Contrato 9.1 imutável e validado à criação (`KnowledgeRecord`,
  `KnowledgeKind`, `KnowledgeMetadata`; `KNOWLEDGE_CONTRACT_VERSION`).
- Datações por `id` único com `wsai.knowledge.duplicate`.
- Heurísticas deterministas (idioma por marcadores, etiquetas por
  frequência com exclusão de palavras de ligação, `"und"` no indeciso).
- Índice invertido com pesos de campo (título 3, etiquetas 2, conteúdo 1)
  e reindexação por substituição.
- Persistência SQLite por `id` (PK), metadados JSON (`ensure_ascii=False`),
  carga ordenada; único I/O introduzido na Fase 9 (decisão documentada).
- Contexto textual determinista (`text()` estável) e ingestão lexical
  (extensões textuais; binários/vazios/oversized ignorados).

## 5. TESTES

Execução real no ambiente de desenvolvimento (2026-09-09):

```text
py -3.12 -m pytest --junitxml
tests=491  failures=0  errors=0  skipped=0
exit code: 0
```

- Base pré-Fase 9: **423** testes intactos (regressão zero).
- Knowledge: **68** testes novos (10 contrato + 8 registo + 14 metadados +
  11 índice + 8 persistência + 8 contexto + 9 ingestão).
- 10/10 testes de contrato arquitectural aprovados (fronteiras e
  subsistemas futuros).

## 6. INTEGRAÇÕES E RECUPERAÇÃO

- Circuito integrado verificado por teste:
  persistir → carregar → admitir → indexar → consultar → contexto.
- Ingestão → registo → índice → contexto verificado end-to-end.
- Reindexação por substituição e `unindex` limpos; persistência com
  substituição por `id`; carga ordenada determinista.
- Sem recuperação externa (não há rede/modelos no âmbito lexical);
  SQLite recuperável por reingestão ou re-carga.

## 7. DOCUMENTAÇÃO

- `docs/validation/FASE9_VALIDATION_REPORT.md` — este relatório, com a
  estrutura oficial de 10 secções.
- BASE-37/38/39/40/41/42/43 por unidade; `ARCHITECTURE.md` 3.9;
  `IMPLEMENTATION_LOG.md` com as unidades 9.1–9.7; `PROJECT_STATE.md`
  reflecte o fecho formal (âmbito lexical).
- `ROADMAP.md` alinhado (unidades 9.1–9.7 concluídas; embeddings como
  decisão terminal).

## 8. PROBLEMAS DETECTADOS

- **K-01 — P3 — RESOLVIDO DURANTE O DESENVOLVIMENTO:** regex de tokenização
  da detecção de idioma descartava marcadores curtos (`de`, `as`);
  separados os regex de detecção (≥2) e de etiquetas (≥3) — resolvido e
  coberto por testes.
- **K-02 — P3 — ABERTO:** relevância é **léxica** (termos), sem semântica
  (embeddings); carência consciente e adiável (decisão material terminal).
- **K-03 — P3 — NÃO BLOQUEANTE:** leitura UTF-8 com `errors="replace"` e
  `rglob` recursivo sem filtros de exclusão — melhorias futuras de baixo
  risco quando a ingestão for afinada.
- **W-01 — P2 — RESOLVIDO:** asserções de teste iniciais do índice e da
  ingestão continham ordenações erradas/confusas; corrigidas durante o
  desenvolvimento.

## 9. DECISÃO FINAL

**APPROVED** — sem P0/P1/P2 bloqueantes; apenas avisos P3 documentados.

A **Fase 9 — Knowledge Engine**, no seu **âmbito lexical (9.1–9.7)**,
fica **formalmente encerrada**.

## 10. PRÓXIMO COMANDO RECOMENDADO

FECHO CONSUMIDO PELO ORQUESTRADOR `/wsai-run`:

1. actualizar `PROJECT_STATE.md` para `FASE 9 CONCLUÍDA` (âmbito lexical);
2. commit final de fecho da Fase 9;
3. opções seguintes: (a) **enriquecimento semântico** (embeddings via
   Model/Provider) — decisão material terminal, requer planeamento próprio
   e decisões documentadas; (b) **Fase 10 — API** (subsistema `api`,
   requer decidir framework HTTP); (c) **Fase 11 — UI**.