# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE METADATA EXTRACTION

## O que foi feito

Foi implementada a **extracção heurística de metadados** do Knowledge
Engine: `KnowledgeMetadataExtractor`, que deriva `KnowledgeMetadata`
estruturado a partir de um `KnowledgeRecord` já válido (contrato 9.1) —
**idioma** (detecção determinista por marcadores), **etiquetas** (termos
frequentes com exclusão de palavras de ligação) e **proveniência**
(preservada do que estiver declarado). É a unidade **Fase 9.3**.

Não foi implementada extracção semântica via Model/Provider, nem
indexação, nem I/O, nem persistência — esses pontos ficam para unidades
posteriores com decisão própria.

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "metadados".
- Reutiliza o contrato 9.1 (`KnowledgeRecord`, `KnowledgeMetadata`) e o
  registo 9.2 (os metadados extraídos alimentarão a admissão).
- Julgamento local do próprio subsistema: nenhuma aresta nova em
  `FRONTEIRAS`.

## Para que serve

- Produzir metadados deterministas (idioma, etiquetas) para cada unidade
  de conhecimento antes da indexação/recuperação.
- Indicar a proveniência (fonte, autor, extras) sem sobrepor o que já
  estiver declarado.
- Preparar o caminho da ingestão: conteúdo + fontes → metadados →
  admissão → indexação.

## Decisão de fronteira

Sem decisão nova. `metadata.py` depende apenas de `knowledge.base`
(contrato interno do subsistema). Nenhuma aresta foi adicionada a
`FRONTEIRAS`; o subsistema mantém a dependência de `core` introduzida no
registo (9.2).

## Ficheiros criados/alterados

- `src/wsai2/knowledge/metadata.py` — `KnowledgeMetadataExtractor`,
  `detect_language`, `derive_tags` (heurísticas puras, deterministas, sem
  estado e sem I/O)
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeMetadataExtractor`
  e as heurísticas
- `tests/test_knowledge_metadata.py` — 14 testes da extracção
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 actualizada com a
  extracção
- `docs/knowledge/BASE-39-knowledge-metadata-extraction.md` — este
  relatório

Nenhum módulo existente das Fases 1–9.2 foi alterado.

## Dependências

- `metadata.py`: `knowledge.base` (mono espacial do próprio subsistema);
  stdlib (`re`, `collections.Counter`).
- Direcção das dependências: permanece dentro do subsistema; nada externo
  depende desta unidade.

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **455 testes aprovados** (14 extracção + 441 prévios).
Regressão da base de 441 testes intacta.

Os testes validam:

- detecção de idioma português/inglês; empate/sem texto → `"und"`;
- extracção completa o idioma em falta e preserva o explícito;
- derivação de etiquetas (exclusão de palavras de ligação, ordem por
  frequência, limite);
- preservação de `source`/`author`/`extras`;
- junção de etiquetas explícitas + derivadas sem duplicar;
- determinismo e tratamento de registos com metadados por omissão.

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO**.

Etapas concluídas:

- 9.1 contrato do subsistema — Knowledge Contract ✓
- 9.2 registo central — Knowledge Registry ✓
- 9.3 extracção de metadados (heurística) — esta unidade ✓

Em falta (unidades posteriores): indexação, recuperação e construção de
contexto.

## Riscos residuais

- A detecção de idioma é heurística (dois idiomas + `"und"`); cobertura
  alargada de idiomas seria aditivo posterior, se necessário.
- Extracção semântica de conhecimento (condensações, sumarização) não foi
  abordada de propósito — exige decisão sobre Model/Provider e
  embeddings, fora do âmbito desta unidade.
- Os metadados são derivados por registo isolado; não há ainda relação
  entre fontes nem deduplicação global (ingestão/indexação posteriores).

## Próximo passo

Fase 9, etapa de **indexação/recuperação**. Esta etapa pode envolver I/O
de armazenamento ou motores de embeddings — **exigirá decisão documentada
antes de qualquer persistência**. Antes disso, a regra de continuação do
`PROJECT_STATE.md` impõe a paragem para decisão, mantendo a
reversibilidade total da Fase 9 até então.