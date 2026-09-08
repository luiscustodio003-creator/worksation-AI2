# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE REGISTRY

## O que foi feito

Foi implementado o **registo central de conhecimento** do Knowledge
Engine: `KnowledgeRegistry`, que admite `KnowledgeRecord` (contrato 9.1)
com **id único**, rejeita duplicações antes da admissão e responde a
consultas (`get`/`has`/`all`/`len`/`unregister`), seguindo o padrão dos
registos das Fases 4–8 (`CapabilityRegistry`, `ModelRegistry`,
`ProviderRegistry`, `ExtensionRegistry`). É a unidade **Fase 9.2**.

Não foi implementada nenhuma lógica de ingestão de ficheiros, extracção,
indexação, pesquisa nem persistência. O registo é um catálogo em memória.

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "admissão do
  conhecimento".
- Base declarativa e interrogação por identidade sobre a qual a ingestão
  (que produzirá registos a partir de fontes), a indexação e a
  recuperação se integrarão em unidades posteriores.
- Reutiliza o `KnowledgeRecord` do contrato 9.1 e a taxonomia de erros
  do núcleo (`ValidationError`, código `wsai.knowledge.duplicate`).

## Para que serve

- Garantir que cada unidade de conhecimento tem um **id único** no
  catálogo, antes de qualquer ingestão ou indexação.
- Dar o padrão de acesso (admitir, consultar, remover) que as unidades de
  recuperação e de contexto usarão.
- Ancorar o registo à versão de contrato suportada
  (`KNOWLEDGE_CONTRACT_VERSION = "1.0"`).

## Decisão de fronteira (autorizada)

O registo consume a taxonomia de erros do núcleo
(`wsai2.core.errors.ValidationError`), tal como todos os registos das
Fases 4–8. Acrescenta **uma** aresta a `FRONTEIRAS`:
`("knowledge", "core")`. Justificação documental: padrão estabelecido
dos registos; dependência para dentro (artigo 2); sem ciclos (o `core`
não depende de `knowledge`).

## Ficheiros criados/alterados

- `src/wsai2/knowledge/registry.py` — `KnowledgeRegistry` (catálogo com
  admissão por id único; `supported_contract_version`)
- `src/wsai2/knowledge/__init__.py` — exporta `KnowledgeRegistry`
- `tests/test_knowledge_registry.py` — 8 testes do registo
- `tests/test_architecture_contract.py` — nova aresta
  `("knowledge", "core")` em `FRONTEIRAS`
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 actualizada com o
  registo
- `docs/knowledge/BASE-38-knowledge-registry.md` — este relatório

Nenhum módulo existente das Fases 1–9.1 foi alterado.

## Dependências

- `registry.py`: `wsai2.core.errors` (taxonomia, já existente) e o
  contrato do próprio subsistema (`knowledge.base`).
- Direcção das dependências: `knowledge` aponta para `core` (centro);
  nada depende de `knowledge`.
- Sem dependências de Runtime/Provider/Capability/Model (constituição,
  artigo 2 — dependências apontam para dentro).

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **441 testes aprovados** (8 registo + 433 base prévia).
Regressão da base de 433 testes intacta.

Os testes validam:

- admissão e preservação por id; objecto devolvido sem cópia;
- rejeição de id duplicado (`wsai.knowledge.duplicate`) sem corromper o
  catálogo;
- versão suportada por defeito (`"1.0"`);
- consultas `get`/`has`/`all`/`len` e ordem de admissão preservada;
- `unregister` (remoção e devolução booleana);
- admissão de tipos distintos (`document`/`note`).

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO**.

Etapas concluídas:

- 9.1 contrato do subsistema — Knowledge Contract ✓
- 9.2 registo central — Knowledge Registry ✓ (esta unidade)

Em falta (unidades posteriores): extracção, metadados dinâmicos,
indexação, recuperação e construção de contexto.

## Riscos residuais

- O catálogo é em memória; a persistência (quando houver decisão
  documentada de armazenamento) é responsabilidade de unidades futuras.
- Não existe ainda pesquisa por conteúdo — responsabilidade das unidades
  de indexação/recuperação.
- A versão suportada é declarativa; a validação de versão por registo é
  aditiva se o contrato evoluir (não exigida nesta unidade).

## Próximo passo

Fase 9 — unidade de **extracção de metadados**: derivar
`KnowledgeMetadata` estruturado a partir do conteúdo/registo e/ou da
fonte (normalização de idioma, etiquetas e proveniência), preparando a
indexação. A extracção semântica (via Model/Provider) permanece para
unidade posterior com decisão própria.