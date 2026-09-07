# WORKSTATION AI 2 — RELATÓRIO DA BASE: TASK INTELLIGENCE (CONTRATO)

## O que foi feito

Foi iniciada a **Fase 7 — Task Intelligence** com o **contrato de
tarefa**: `TaskKind` (tipos funcionais chat, completion, embedding) e
`Task` — a representação imutável do pedido de trabalho, com texto,
máximo de tokens, capacidades exigidas e metadados opacos.

## Onde se encaixa na arquitectura

Item *contrato de tarefa* do roadmap da **Fase 7 — Task Intelligence**
(subsistema 3.7). A auditoria BASE-19 define esta como a primeira
unidade da nova fase, antes da classificação, requisitos, selecção de
capacidades e plano de execução.

A tarefa é independente de fornecedores e modelos (constituição,
artigo 13): apenas declara **o que** o sistema deve fazer; **quem**
(o modelo e o fornecedor) é decidido em unidades posteriores pelo fluxo
modelo → fornecedor da arquitectura.

## Para que serve

- Representa, de forma uniforme, qualquer trabalho pedido ao sistema
  (diálogo, geração livre, embeddings).
- Declara as capacidades exigidas para o plano (Capability Engine) e o
  tipo funcional que alinha com as categorias de modelo (CHAT /
  COMPLETION / EMBEDDING).
- Carrega metadados opacos (contexto), sem que o domínio os interprete.

## Ficheiros criados/alterados

- `src/wsai2/task/base.py` — `TaskKind`, `Task`
- `src/wsai2/task/__init__.py` — exports públicos
- `tests/test_task.py`
- `docs/task/BASE-20-task-intelligence-contract.md`

## Dependências

- Domínio puro; sem dependências de plataforma ou de terceiros.
- Alinhamento semântico com `wsai2.model` (categorias de modelo) — sem
  importação (dependência apenas conceptual, evitando acoplamento).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **179 testes aprovados** (9 task + 46 provider + 42 model +
33 capability + 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- criação com valores por defeito; imutabilidade;
- os três tipos funcionais;
- capacidades exigidas conservadas; metadados opacos; max_tokens;
- rejeição de prompt vazio e de max_tokens inválido;
- resumo textual.

## Estado da fase

**Fase 7 — Task Intelligence** — **EM PROGRESSO**.

Itens do roadmap implementados:

- contrato de tarefa ✓

Itens pendentes:

- classificação de tarefas;
- requisitos de tarefa;
- selecção de capacidades;
- plano de execução.

## Próximo passo

Unidade seguinte da Fase 7: **classificação de tarefas** — atribuir a
cada tarefa a categoria funcional de modelo mais adequada (chat /
completion / embedding), preparando a selecção de modelo e fornecedor.