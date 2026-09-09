# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE SQLITE PERSISTENCE

## O que foi feito

Foi implementada a **persistência SQLite do conhecimento** do Knowledge
Engine: `KnowledgeStore`, que guarda e carrega `KnowledgeRecord`
(contrato 9.1) por ``id`` (chave primária), com metadados serializados em
JSON, num ficheiro SQLite local (stdlib `sqlite3`, transversal a
Windows/Linux). É a unidade **Fase 9.5 — recuperação (persistência)**.

O armazenamento não pesquisa nem indexa; alimenta o `KnowledgeRegistry`
(9.2) e o `KnowledgeIndex` (9.4) para a consulta em memória. O ciclo
integrado **persistir → carregar → admitir → indexar → consultar** está
verificado por teste.

## Decisão documentada (consulta ao orquestrador)

A unidade 9.5 foi o ponto de adiamento da decisão de armazenamento feito
em 9.4. A decisão tomada (2026-09-09), registada após consulta, foi:

> **Persistência SQLite local** — guardar e carregar os registos do
> contrato 9.1 de um ficheiro SQLite, por id, como estratégia de
> armazenamento da recuperação. Motivação: stdlib (sem novas
> dependências), transversal a Windows/Linux, consultável e auditável,
> com esquema explícito e substituição por id.

Consequências da decisão:

- a Fase 9 passa a ter **I/O e estado persistente** (ficheiro `.db`);
- a **reversibilidade** mantém-se ao nível da implementação: o módulo é
  removível, o ficheiro é apagável e nenhum código externo depende do
  armazenamento;
- o CLI/API (fora de âmbito da Fase 9) usará o caminho do ficheiro ou um
  directório de projecto quando existir;
- **embeddings continuam fora desta unidade**: a recuperação semântica,
  se for decidida, será uma fase posterior com decisão própria.

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "recuperação
  (armazenamento)".
- Consome `KnowledgeRecord`/`KnowledgeKind`/`KnowledgeMetadata` (9.1) e é
  consumido pela recuperação via `KnowledgeRegistry`/`KnowledgeIndex`.
- Dependências: `sqlite3`, `json`, `pathlib`, `contextlib` — só stdlib.
  **Nenhuma aresta nova** em `FRONTEIRAS`.

## Para que serve

- Tornar o conhecimento admitido **persistente entre execuções** (a
  limitação consciente do índice em memória da 9.4).
- Recuperar registos (por id, ordenados, reconstruindo tipos e
  metadados) para reconstruir registo e índice no arranque.
- Substituir pelo id (re-ingestão), remover e contar com transacções
  simples e deterministas.

## Ficheiros criados/alterados

- `src/wsai2/knowledge/storage.py` — `KnowledgeStore` (save/save_all/
  delete/count/load, `path`; esquema `knowledge_record`; serialização
  JSON de etiquetas/extras com `ensure_ascii=False`)
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeStore`
- `tests/test_knowledge_storage.py` — 8 testes do armazenamento
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 actualizada com a
  persistência
- `docs/knowledge/BASE-41-knowledge-sqlite-persistence.md` — este
  relatório (registo da decisão)

Nenhum módulo das Fases 1–9.4 sofreu alteração de comportamento.

## Dependências

- `storage.py`: stdlib (`sqlite3`, `json`, `pathlib`, `contextlib`) e o
  contrato do próprio subsistema (`knowledge.base`).
- Direcção das dependências: permanece no subsistema; nada externo
  depende desta unidade. Sem Runtime, extensões ou fornecedores.

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **474 testes aprovados** (8 armazenamento + 466 prévios).
Regressão da base de 466 testes intacta.

Os testes validam:

- ciclo completo guardar→carregar (identidade, título, conteúdo, tipo,
  metadados, etiquetas, extras, `created_at`);
- substituição pelo id (sem duplicar);
- `delete` (booleano), `count` e armazenamento vazio;
- criação do ficheiro e do esquema (`knowledge_record`) e `path`;
- ordem de carga determinista pelo id;
- caracteres acentuados preservados no ciclo;
- recuperação integrada: persistir→carregar→registo→índice→consulta.

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO**.

Etapas concluídas:

- 9.1 contrato do subsistema ✓
- 9.2 registo central ✓
- 9.3 extracção de metadados (heurística) ✓
- 9.4 indexação em memória ✓
- 9.5 recuperação (persistência SQLite) ✓ (esta unidade)

Em falta (unidades posteriores): construção de contexto (9.6).

## Riscos residuais

- **I/O introduzido**: o ficheiro `.db` é estado persistente; a criação do
  directório pai e o esquema são automáticos, mas o caminho deve estar
  num local com permissões de escrita (a decidir no CLI/API).
- Concorrência multi-processo sobre o mesmo ficheiro não é garantida
  (aplicação é single-process; transacções por operação cobrem o uso
  actual).
- A recuperação é léxico-espacial via índice em memória; **semântica
  (embeddings) está deliberadamente fora desta unidade**.
- O formato interno da tabela é estável nesta versão; migrações de
  esquema ficariam a cargo de unidades futuras.

## Próximo passo

Fase **9.6 — construção de contexto**: montar, a partir da consulta ao
índice e dos registos recuperados (persistidos), um pacote de contexto
textual determinista (títulos, excertos, proveniência e etiquetas
relevantes). É uma unidade pura, directamente dependente de 9.4/9.5, sem
decisão material nova.