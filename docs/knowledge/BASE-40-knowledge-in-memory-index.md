# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE IN-MEMORY INDEX

## O que foi feito

Foi implementada a **indexação em memória** do Knowledge Engine:
`KnowledgeIndex`, um índice invertido que mapeia termos normalizados →
frequência por campo/registo (título, etiquetas, conteúdo) e responde a
consultas por termos com **ordenação determinista**. É a unidade
**Fase 9.4**.

O índice é construído com a mesma normalização de termos do resto do
subsistema (`tokenize`), é totalmente **em memória, determinista e
reversível** e não cria I/O, persistência nem embeddings.

## Decisão documentada (consulta ao orquestrador)

A unidade 9.4 estava marcada no `PROJECT_STATE.md` como interrompida até
decisão sobre **estratégia de armazenamento/embeddings**. A decisão
tomada (2026-09-09) foi:

> **Índice em memória puro** — construir e interrogar integralmente em
> memória (reversível, sem I/O, persistência ou embeddings). A estratégia
> de armazenamento persistente e/ou embeddings da recuperação fica para a
> unidade 9.5, com decisão própria, antes de qualquer persistência.

Esta decisão está registada aqui e em `PROJECT_STATE.md`. Nenhuma
persistência é criada antes da decisão de armazenamento.

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "indexação".
- Consome `KnowledgeRecord` (9.1) e `KnowledgeRegistry` (9.2) por
  composição em memória; usa a normalização partilhada `tokenize` (9.3).
- Dependências internas ao subsistema: **nenhuma aresta nova** em
  `FRONTEIRAS`.

## Para que serve

- Permitir a consulta por termos sobre o conhecimento admitido, com
  priorização de campos (título 3, etiquetas 2, conteúdo 1).
- Servir de base determinista à recuperação/construção de contexto
  (9.5/9.6), sem depender de fornecedores nem de armazenamento.
- Reindexação por substituição e remoção limpa, mantendo o catálogo
  coerente com o registo.

## Ficheiros criados/alterados

- `src/wsai2/knowledge/index.py` — `KnowledgeIndex` (build/index/unindex/
  search/len), com pesos de campo e ordenação determinista
- `src/wsai2/knowledge/metadata.py` — `tokenize()` público (normalização
  partilhada de termos); `derive_tags` passa a usá-la (mesmo
  comportamento)
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeIndex` e `tokenize`
- `tests/test_knowledge_index.py` — 11 testes do índice
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 actualizada com o
  índice
- `docs/knowledge/BASE-40-knowledge-in-memory-index.md` — este relatório

Nenhum módulo das Fases 1–9.3 sofreu alteração de comportamento.

## Dependências

- `index.py`: `knowledge.base`, `knowledge.registry`, `knowledge.metadata`
  (mono espacial do subsistema) e stdlib (`collections.defaultdict`).
- Direcção das dependências: permanece dentro do subsistema; nada externo
  depende desta unidade. Sem Runtime, extensões ou fornecedores.

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **466 testes aprovados** (11 índice + 455 prévios).
Regressão da base de 455 testes intacta.

Os testes validam:

- indexação e consulta por termos do conteúdo;
- consultas sem correspondência / vazias → tuplo vazio;
- normalização partilhada (casefold) entre conteúdo e consulta;
- pesos de campo: título acima de conteúdo; etiquetas somam peso;
- reindexação por substituição (sem acumular) e `unindex` limpo;
- `build` a partir de `KnowledgeRegistry`;
- ordenação determinista (pontuação e `id` em caso de empate);
- limite de resultados e índice vazio.

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO**.

Etapas concluídas:

- 9.1 contrato do subsistema ✓
- 9.2 registo central ✓
- 9.3 extracção de metadados (heurística) ✓
- 9.4 indexação em memória ✓ (esta unidade)

Em falta (unidades posteriores): **recuperação (9.5)** e construção de
contexto (9.6).

## Riscos residuais

- O índice é apenas léxico (termos), sem semântica; relevância semântica
  exigiria embeddings (decisão adiada para 9.5).
- Em memória: sem persistência de ficheiro, o conhecimento indexado
  perde-se no ciclo do processo — consciente e reversível; a persistência
  é a decisão adiada.
- A detecção de termos usa a gramática de ≥ 3 letras; termos com 1–2
  letras não são indexáveis (coerente com extracção/etiquetas).

## Próximo passo

Fase **9.5 — recuperação/construção de contexto**. Esta etapa foi o ponto
de adiamento da decisão de **armazenamento persistente e/ou embeddings**:
antes de qualquer I/O ou motor de embeddings, é necessária decisão
documentada (ver `PROJECT_STATE.md`, regra de continuação). O índice em
memória (9.4) já fornece base determinista consultável para a construção
de contexto inicial.