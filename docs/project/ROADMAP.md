# WORKSTATION AI 2 — ROADMAP DE DESENVOLVIMENTO

## Fase 0 — Fundação e Governação

- estrutura mínima do projecto;
- documentação arquitectural;
- regras globais;
- comando `/wsai-run`;
- família de comandos `/wsai-*` para execução individual das etapas;
- skill de desenvolvimento;
- política de modelos OpenCode;
- política Git;
- estado persistente;
- base de testes;
- ciclo controlado **AUDITAR → PLANEAR → IMPLEMENTAR → TESTAR → DOCUMENTAR → GIT**.

## Fase 1 — Platform Foundation

- detecção do sistema operativo;
- abstracção de plataforma;
- adaptadores Windows;
- adaptadores Linux;
- testes de compatibilidade.

## Fase 2 — Hardware Intelligence

- CPU;
- memória;
- GPU;
- armazenamento;
- perfil de hardware;
- capacidades estruturais.

## Fase 3 — Runtime Intelligence

- recursos disponíveis;
- carga;
- processos;
- estado de execução;
- perfil de runtime.

## Fase 4 — Capability Engine

- definições de capacidade;
- registo;
- avaliação;
- compatibilidade;
- capacidades disponíveis.

## Fase 5 — Model Intelligence

- registo de modelos;
- metadados;
- requisitos;
- compatibilidade;
- classificação;
- recomendação.

## Fase 6 — Provider Layer

- contratos de fornecedor;
- detecção;
- adaptadores de runtime;
- health checks.

## Fase 7 — Task Intelligence

- modelo de tarefa;
- classificação;
- extracção de requisitos;
- selecção de capacidades;
- plano de execução.

## Fase 8 — Runtime Engine

A Fase 8 começou pela **baseline e auditoria**, não por uma reescrita. O Runtime consome o `ExecutionPlan` já produzido pelo Task Intelligence.

### Preparação e hardening controlado

- auditoria da base existente;
- contratos mínimos de extensão quando necessários;
- modelo de erros transversal quando necessário;
- `ExecutionContext`;
- governação de recursos;
- timeout;
- cancelamento;
- recuperação;
- scheduler;
- gestor de execução;
- monitorização;
- lifecycle e compatibilidade;
- testes de contrato arquitectural;
- Security / Policy;
- Project Isolation;
- Gate — Core pronto para addons.

### Runtime funcional

- scheduler;
- gestor de execução;
- recursos;
- memória;
- cancelamento;
- timeout;
- monitorização;
- concorrência opcional entre planos;
- filas multicamadas com prioridade, backlog e preempção de trabalho pendente.

A ordem concreta das unidades e dos residuais é determinada pelo `PROJECT_STATE.md` e pelo plano de hardening, após auditoria de cada responsabilidade já existente.

**Estado actual:** implementação funcional da Fase 8 concluída, incluindo os três residuais Via B (monitorização, concorrência e filas multicamadas). O fecho formal depende da validação final da fundação e do respectivo relatório persistente.

## Fase 9 — Knowledge Engine

- ingestão;
- extracção;
- metadados;
- indexação;
- recuperação;
- contexto.

**Entrada condicionada:** só iniciar depois de a Fase 8 estar formalmente aprovada pelo `/wsai-validate foundation`.

## Fase 10 — API

- health;
- system;
- hardware;
- runtime;
- capabilities;
- models;
- tasks;
- knowledge.

## Fase 11 — UI

- dashboard;
- hardware;
- modelos;
- capacidades;
- tarefas;
- runtime;
- conhecimento.

## Política de execução

Cada fase será dividida em unidades pequenas e verificáveis. O comando `/wsai-run` executa autonomamente uma unidade já determinada, passando por pre-flight, planeamento, implementação, validação, documentação e Git.

Os comandos `/wsai-audit`, `/wsai-plan`, `/wsai-implement`, `/wsai-test`, `/wsai-validate`, `/wsai-doc` e `/wsai-git` permitem executar essas etapas individualmente.

Nenhuma nova responsabilidade deve ser criada sem primeiro verificar se já existe um componente responsável. Alterações estruturais devem ser incrementais e reversíveis.

### Regra de transição entre fases

```text
ROADMAP — fase macro
      ↓
PROJECT_STATE — unidade concreta / estado real
      ↓
Código + testes + documentação
      ↓
/wsai-validate foundation
      ↓
FOUNDATION APPROVED
      ↓
próxima fase
```

O Roadmap define as fases macro. O `PROJECT_STATE.md` define a unidade concreta e a ordem operacional dentro de uma fase. Esta separação evita que uma alteração incremental e previamente decidida dentro da Fase 8 seja confundida com avanço prematuro para a Fase 9.
