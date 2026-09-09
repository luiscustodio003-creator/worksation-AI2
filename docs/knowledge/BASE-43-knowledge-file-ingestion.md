# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE FILE INGESTION

## O que foi feito

Foi implementada a **ingestão de ficheiros de texto do projecto** do
Knowledge Engine: `FileIngestor`, que percorre um directório raiz, lê os
ficheiros de texto suportados (`.md`, `.py`, `.txt`, `.json`, `.toml`,
`.yaml`, `.yml`) e produz `KnowledgeRecord` (tipo `document`, contrato
9.1) com proveniência relativa e metadados derivados pelo extractor (9.3):
idioma e etiquetas heurísticos. É a unidade **Fase 9.7** (item de roadmap
"ingestão de ficheiros do projecto").

A ingestão é **lexical**: não recorre a embeddings nem a Model/Provider.
Ficheiros binários, vazios ou acima do limite de tamanho são ignorados,
sem falhar, e a ordem de saída é determinista (caminho relativo).

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "ingestão".
- Consome o contrato 9.1 e o extractor de metadados 9.3; produz registos
  prontos a admitir no registo (9.2), persistir (9.5), indexar (9.4) e
  contextualizar (9.6).
- Dependências: `pathlib` e o mono espacial do subsistema.
  **Nenhuma aresta nova** em `FRONTEIRAS`.

## Para que serve

- Transformar a documentação/código do projecto em conhecimento
  consultável, fechando o circuito **ficheiro → registo → metadados →
  índice → persistência → contexto**.
- Fornecer a base determinista sobre a qual o enriquecimento semântico
  (embeddings), quando decidido, será aditivo.

## Ficheiros criados/alterados

- `src/wsai2/knowledge/ingest.py` — `FileIngestor` (ingest com
  `limite_bytes`; `_para_registo` reutiliza `KnowledgeMetadataExtractor`)
- `src/wsai2/knowledge/__init__.py` — exporta `FileIngestor`
- `tests/test_knowledge_ingest.py` — 9 testes da ingestão
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 actualizada
- `docs/knowledge/BASE-43-knowledge-file-ingestion.md` — este relatório

Nenhum módulo das Fases 1–9.6 sofreu alteração de comportamento.

## Dependências

- `ingest.py`: `knowledge.base`, `knowledge.metadata` (mono espacial do
  subsistema) e stdlib (`pathlib`).
- Direcção das dependências: permanece no subsistema; nada externo
  depende desta unidade. Sem Runtime, extensões, fornecedores ou I/O
  fora da leitura pedida.

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **491 testes aprovados** (9 ingestão + 482 prévios).
Regressão da base de 482 testes intacta.

Os testes validam:

- produção de registos `document` com proveniência relativa;
- ordem determinista por caminho (e repetibilidade);
- id derivado do caminho relativo (`km.f.<caminho>`);
- título/idioma/etiquetas derivados (pt-PT, tags não vazias);
- extensões não suportadas e ficheiros vazios ignorados;
- limite de tamanho respeitado;
- directoria vazia → tuplo vazio;
- integração ingestão → registo → índice → contexto;
- metadados do contrato (`KnowledgeMetadata`).

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO (âmbito lexical completo)**.

Etapas concluídas:

- 9.1–9.6 núcleo reversível (contrato, registo, metadados, índice,
  persistência, contexto) ✓
- 9.7 ingestão de ficheiros do projecto (lexical) ✓ (esta unidade)

Ponto de decisão seguinte: enriquecimento semântico (embeddings via
Model/Provider).

## Riscos residuais

- Ingestão **lexical**: a relevância depende de termos, não de semântica;
  oss embeddings são o aditivo natural e exigem decisão própria.
- Leitura UTF-8 com `errors="replace"`: ficheiros mal codificados podem
  perder caracteres sem falhar.
- `rglob` percorre recursivamente; directórios muito grandes exigirão
  filtros/progresso no futuro (fora do núcleo).

## Próximo passo

**Ponto de decisão terminal da Fase 9 (âmbito lexical concluído)**:
enriquecimento semântico com **embeddings via Model/Provider** — exige
decisões documentadas de modelo/fornecedor, integração com o Provider
Layer/Runtime e definição de admissão/aditividade sobre o índice léxico.
Não é executável autonomamente numa unidade do núcleo reversível.