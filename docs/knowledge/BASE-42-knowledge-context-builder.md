# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE CONTEXT BUILDER

## O que foi feito

Foi implementada a **construção de contexto** do Knowledge Engine:
`ContextBuilder`, que monta, a partir da consulta ao `KnowledgeIndex`
(9.4) e dos registos recuperados (9.5), um `KnowledgeContext` textual
**determinista** — entradas por relevância com título, excerto truncado
(com elipse), proveniência e etiquetas, mais uma representação textual
estável (`text()`). É a unidade **Fase 9.6**, que fecha o plano delineado
para o núcleo reversível da Fase 9.

Esta unidade não invoca modelos, não faz I/O e não depende de
fornecedores — apenas serializa texto.

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "contexto".
- Consome `KnowledgeIndex` (9.4) e `KnowledgeRecord` (9.1); as entradas
  podem ser alimentadas por registos persistidos (9.5).
- Dependências internas ao subsistema: **nenhuma aresta nova** em
  `FRONTEIRAS`.

## Para que serve

- Produzir o **pacote de contexto** que, numa integração posterior, será
  fornecido a um modelo — sem acoplar esta unidade a Model/Provider.
- Garantir excertos, título, fonte e etiquetas **estáveis e
  deterministas** (mesma consulta, mesmo índice → mesmo texto).
- Permitir a validação do circuito completo da fase:
  **contrato → registo → metadados → índice → persistência → contexto**.

## Ficheiros criados/alterados

- `src/wsai2/knowledge/context.py` — `ContextBuilder` (build com
  `top`/`snippet_caracteres`), `ContextEntry`, `KnowledgeContext` (com
  `text()`)
- `src/wsai2/knowledge/__init__.py` — exporta `ContextBuilder`,
  `ContextEntry` e `KnowledgeContext`
- `tests/test_knowledge_context.py` — 8 testes do constructor de contexto
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 actualizada com o
  contexto
- `docs/knowledge/BASE-42-knowledge-context-builder.md` — este relatório

Nenhum módulo das Fases 1–9.5 sofreu alteração de comportamento.

## Dependências

- `context.py`: `knowledge.base`, `knowledge.index` (mono espacial do
  próprio subsistema) e stdlib (`dataclasses`).
- Direcção das dependências: permanece no subsistema; nada externo
  depende desta unidade. Sem Runtime, extensões, fornecedores ou I/O.

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **482 testes aprovados** (8 contexto + 474 prévios).
Regressão da base de 474 testes intacta.

Os testes validam:

- entradas seguem a ordem de relevância do índice;
- título/fonte/etiquetas acompanham a entrada;
- truncamento de excertos com elipse final e excertos curtos íntegros;
- consulta sem correspondências → contexto vazio com `query` mantida;
- limite `top` respeitado;
- `text()` inclui consulta/título/excerto e é determinista;
- a pontuação do título lidera a posição das entradas.

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO (núcleo reversível completo)**.

Etapas concluídas:

- 9.1 contrato do subsistema ✓
- 9.2 registo central ✓
- 9.3 extracção de metadados (heurística) ✓
- 9.4 indexação em memória ✓
- 9.5 recuperação (persistência SQLite) ✓
- 9.6 construção de contexto ✓ (esta unidade — fecha o circuito)

Em falta (decisão de âmbito): **ingestão de ficheiros do projecto e
extracção semântica real** (embeddings via Model/Provider) — exige
planeamento próprio e decisões documentadas (não é o núcleo reversível).

## Riscos residuais

- O contexto é **léxico** (excertos por relevância de termos); sem
  semântica/embeddings, ainda não soma o potencial de RAG — decisão
  adiada.
- O `text()` usa um formato próprio e estável; consumidores externos
  devem usar a API (Campos) ou `text()` sem depender de markdown preciso.
- A ingestão de ficheiros reais (ler `docs/`, `src/`) é a fronteira
  seguinte e envolverá decisões de leitura/tokenização/pesos — fora do
  núcleo reversível deste documento.

## Próximo passo

A Fase 9 está **funcionalmente completa no núcleo reversível**: contrato,
registo, metadados, índice, persistência e contexto estão prontos e
verificados. A **ingestão semântica real** (ler ficheiros do projecto e
enriquecer com embeddings via Model/Provider) é o próximo ponto de
decisão — exige planeamento próprio e decisões documentadas antes de
motores de embeddings.