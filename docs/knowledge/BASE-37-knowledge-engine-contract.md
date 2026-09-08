# WORKSTATION AI 2 — RELATÓRIO DA BASE: KNOWLEDGE ENGINE CONTRACT

## O que foi feito

Foi definido o **contrato declarativo mínimo do Knowledge Engine** do
WorkStation AI 2: a classificação do conhecimento (`KnowledgeKind`), os
metadados estruturados (`KnowledgeMetadata`) e o registo de conhecimento
imutável (`KnowledgeRecord`), além da versão de contrato
`KNOWLEDGE_CONTRACT_VERSION = "1.0"`. É a unidade **Fase 9.1**, a primeira
unidade implementável da **Fase 9 — Knowledge Engine** (subsistema 3.9),
autorizada após o fecho formal da Fase 8 (gate de fundação).

Não foi implementada nenhuma lógica de ingestão, extracção, indexação,
recuperação ou construção de contexto. O contrato é puramente declarativo
e imutável.

## Onde se encaixa na arquitectura

- **Fase 9 — Knowledge Engine** (subsistema 3.9), etapa "contrato do
  subsistema".
- Base declarativa sobre a qual a extracção (que poderá consumir Model
  Intelligence / Provider Layer via Runtime), a indexação, a recuperação
  e a construção de contexto se integrarão em unidades posteriores.
- O contrato **não acopla** a unidade ao Capability Engine, Provider
  Layer ou Model Intelligence: as fontes são referidas por identificador
  textual (`source`), de modo reversível (constituição, artigo 8 —
  crescimento controlado).

## Para que serve

- Declarar, de forma estável e validada, o que uma unidade de
  conhecimento é, antes de qualquer ingestão, indexação ou pesquisa.
- Servir de base ao fluxo da Fase 9:

```text
ingestão → extracção → metadados → indexação → recuperação → contexto
```

- Estabelecer a taxonomia de origem do conhecimento (document/extract/note)
  para as unidades de extracção e de construção de contexto.

## Decisão de fronteira (autorizada)

O subsistema `knowledge` **deixa de constar** de `SUBSISTEMAS_FUTUROS` no
teste de contrato arquitectural (passa a `api`/`ui`, Fases 10–11). A
justificação documental: a Fase 9 está autorizada no estado persistente
(`PROJECT_STATE.md`) e no roadmap; `knowledge` é **folha** nesta unidade
(só stdlib) e não adiciona arestas a `FRONTEIRAS`.

## Ficheiros criados/alterados

- `src/wsai2/knowledge/base.py` — `KNOWLEDGE_CONTRACT_VERSION`,
  `KnowledgeKind`, `KnowledgeMetadata`, `KnowledgeRecord` (frozen,
  validado em `__post_init__`)
- `src/wsai2/knowledge/__init__.py` — exports públicos do submódulo
- `tests/test_knowledge.py` — 10 testes do contrato
- `tests/test_architecture_contract.py` — `knowledge` sai de
  `SUBSISTEMAS_FUTUROS` (justificação documentada)
- `docs/architecture/ARCHITECTURE.md` — secção 3.9 expandida; secção 7
  actualizada para Fase 8 fechada e Fase 9 em curso
- `docs/architecture/BASE-31-architecture-contract-tests.md` — regra 9
  alinhada com a autorização de `knowledge`
- `docs/knowledge/BASE-37-knowledge-engine-contract.md` — este relatório

Nenhum módulo existente das Fases 1–8 foi alterado.

## Dependências

- `base.py`: apenas stdlib (`dataclasses`, `enum`).
- Direcção das dependências: `knowledge` é um módulo **folha** nesta
  unidade — depende de nada do domínio e é consumido por unidades
  posteriores da Fase 9.
- Sem dependências de Runtime/Provider/Capability/Model (constituição,
  artigo 2 — dependências apontam para dentro).

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **433 testes aprovados** (10 knowledge + 423 base prévia).
Regressão da base de 423 testes intacta.

Os testes validam:

- construção de registo completo (todos os campos);
- defaults aplicados (metadados e `created_at` vazios);
- imutabilidade (`frozen`);
- validação de `id`/`title`/`content`/`kind` → erro;
- enums de tipo com as categorias document/extract/note;
- versão de contrato declarada;
- resumo textual do registo.

## Estado da fase

**Fase 9 — Knowledge Engine — EM CURSO**.

Etapa concluída:

- 9.1 contrato do subsistema — Knowledge Contract ✓ (esta unidade)

Em falta (unidades posteriores): ingestão, extracção, metadados
dinâmicos, indexação, recuperação e construção de contexto.

## Riscos residuais

- `KnowledgeKind` é uma lista aberta de categorias conhecidas, não
  fechada; poderá evoluir em unidades posteriores sem mudança de contrato.
- `KnowledgeMetadata` é declarativo; a extracção automática de metadados
  e a normalização de fontes são responsabilidade de unidades posteriores.
- Não existe ainda validação de duplicação de `id` nem de pesquisa —
  responsabilidade das unidades de ingestão/indexação e recuperação.

## Próximo passo

Fase 9 — unidade de **metadados/ingestão do contrato**: evoluir o
`KnowledgeRegistry` (registo central de `KnowledgeRecord`, padrão dos
registos das Fases 4–8) e a admissão de registos por identificador
(duplicações rejeitadas), antes da extracção e da indexação.