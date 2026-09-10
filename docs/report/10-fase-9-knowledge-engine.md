# WORKSTATION AI 2 — RELATÓRIO DA FASE 9

## KNOWLEDGE ENGINE

**Subsistema:** `wsai2.knowledge`
**Referência arquitectural:** subsistema 3.9
**Roadmap:** Fase 9 (unidades 9.1–9.7)
**Estado actual:** FECHADA no **âmbito lexical** — gate **APPROVED** (2026-09-09), relatório em `docs/validation/FASE9_VALIDATION_REPORT.md`. O enriquecimento semântico (embeddings) é uma **decisão material terminal** com planeamento próprio.

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

O WSAI 2 trata a gestão de conhecimento como um subsistema próprio: **ingerir ficheiros, extrair metadados, indexar, recuperar e construir contexto** para tarefas de IA.

O problema que a Fase 9 resolve é dar ao sistema **memória documental** — transformar os documentos do utilizador em conhecimento pesquisável que pode alimentar o contexto das tarefas.

## 2. O ÂMBITO (LEXICAL / SEMÂNTICO)

Existem duas camadas de recuperação de informação:

- **Recuperação lexical** — por termos e pesos de campo. Implementada (9.1–9.7).
- **Recuperação semântica** — por significado, usando embeddings via Model/Provider. **Não implementada** — é a decisão material terminal (Ramo D).

O fecho formal da Fase 9 respeita esta fronteira: o núcleo reversível está completo no âmbito **lexical**; a semântica exige modelo/fornecedor e integração com o Provider Layer, com planeamento próprio.

## 3. ARQUITECTURA DA FASE (CIRCUITO LEXICAL)

```text
wsai2.knowledge
  ├── base.py      → marca de contrato: KnowledgeKind, KnowledgeMetadata, KnowledgeRecord (imutável)
  ├── registry.py  → KnowledgeRegistry: admissão por id único
  ├── metadata.py  → KnowledgeMetadataExtractor: idioma + etiquetas (heurístico, determinista)
  ├── index.py     → KnowledgeIndex: índice invertido em memória com pesos de campo
  ├── storage.py   → KnowledgeStore: persistência SQLite local
  ├── context.py   → ContextBuilder / KnowledgeContext: pacote textual determinista
  └── ingest.py    → FileIngestor: leitura lexical de ficheiros de texto do projecto
```

### O circuito fechado

```text
ficheiro
  → contrato (9.1)
  → registo (9.2)
  → metadados (9.3)
  → índice (9.4)
  → persistência (9.5)
  → contexto (9.6)
```

Tudo com **apenas stdlib** (`sqlite3`, `json`, `pathlib`, `re`, `collections`, `dataclasses`), mais a taxonomia de erros do Core. Determinismo garantido por ordenações explícitas.

## 4. DECISÕES ARQUITECTURAIS RELEVANTES

- **9.4 — índice em memória puro** (sem I/O nem persistência nesta unidade), com reindexação por substituição.
- **9.5 — persistência SQLite local** — decisão de armazenamento documentada; os registos reconstroem registo e índice no arranque.
- **9.7 — ingestão lexical** — extensões textuais (.md/.py/.txt/.json/.toml/.yaml/.yml); binários/vazios/oversized ignorados.
- **Idioma e etiquetas por heurística determinista** — sem modelos; `"und"` no indeciso.

## 5. CONEXÃO COM A VISÃO

>A visão planeia o ecossistema de addons em torno de capacidades como PDF, RAG, embeddings e bases vectoriais. A Fase 9 é a fundação desse caminho **dentro do núcleo lexical**: o contrato, o registo, o índice e o contexto que qualquer addon futuro (RAG, PDF, voz, visão) poderá consumir.

Também demonstra a regra "Core pequeno": a recuperação semântica (que exigiria modelos e I/O externo) **não** entra no núcleo lexical — permanece como decisão própria e planeamento dedicado.

## 6. EVIDÊNCIA E VALIDAÇÃO

- Gate da Fase 9: `tests=491, failures=0` no fecho; **APPROVED** sem P0/P1/P2.
- 68 testes novos de Knowledge (10 contrato + 8 registo + 14 metadados + 11 índice + 8 persistência + 8 contexto + 9 ingestão); regressão zero sobre a base de 423.
- Circuito integrado verificado end-to-end: persistir → carregar → admitir → indexar → consultar → contexto.
- Avisos P3 documentados (não bloqueantes): relevância lexical sem semântica (K-02); leitura UTF-8 `errors="replace"` e `rglob` sem exclusões (K-03).

## 7. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: dar ao sistema memória documental — conhecimento pesquisável que alimenta tarefas.
2. Solução: subsistema Knowledge — contrato, registo, metadados, índice, persistência, contexto e ingestão.
3. O circuito lexical fecha com stdlib pura: ficheiro → contexto.
4. Duas camadas separadas: recuperação **lexical** (feita) e **semântica/embeddings** (decisão material terminal).
5. Papel no sistema: é a fundação que os addons futuros (RAG, PDF, voz, visão) vão consumir — sem crescer o Core.