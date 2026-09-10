# WORKSTATION AI 2 — RELATÓRIO DE FASES DO PROJECTO

## Visão geral, índice e guia de utilização

**Versão:** Setembro de 2026
**Finalidade:** apresentar, numa colecção de documentos autónomos, a razão de existir de cada fase do WorkStation AI 2, a sua arquitectura, os seus componentes e o seu estado actual, para alimentar materiais de explicação (vídeos NotebookLM, apresentações e documentação pública).
**Estado de referência da suíte:** 528/528 testes verdes no momento deste relatório.

---

## 1. O QUE É O WSAI 2

O WorkStation AI 2 (WSAI 2) é uma **plataforma local e multiplataforma de inteligência artificial** construída sobre uma ideia central:

> "Em vez de obrigar o utilizador a adaptar o computador à IA, fazer com que a IA compreenda o computador e se adapte aos recursos que realmente existem."

O WSAI 2 não pretende ser **mais um runtime de IA local** (como Ollama, llama.cpp, LM Studio, LocalAI ou vLLM). Pretende ocupar uma camada diferente e mais alta: a **camada de inteligência de decisão** que decide **o quê**, **com que modelo**, **através de que motor** e **com que recursos** uma tarefa deve ser executada, conhecendo previamente a máquina, o estado momentâneo dos seus recursos e a natureza da tarefa.

Os motores existentes continuam a ser utilizados, mas como **providers** atrás de contratos estáveis. O WSAI 2 acrescenta o que eles não fornecem: a inteligência sobre a execução.

### Frase-chave do projecto

> "WSAI2 não pretende ser apenas mais um runtime de IA local. Pretende ser a camada de inteligência que decide como a IA deve ser executada."

---

## 2. O PIPELINE DE INTELIGÊNCIA (A ARQUITECTURA EM FLUXO)

O sistema funciona como uma cadeia de decisões. Cada elo é um subsistema com responsabilidade própria:

```text
Pedido
  ↓
Task Intelligence        → O que esta tarefa exige?
  ↓
Hardware Intelligence    → O que esta máquina suporta?
  ↓
Runtime Intelligence     → O que está disponível neste momento?
  ↓
Capability Engine        → Que capacidades podem realmente ser usadas?
  ↓
Model Intelligence       → Que modelo é adequado?
  ↓
Provider Layer           → Que provider/backend pode executar esse modelo?
  ↓
Execution Planner        → Qual a melhor estratégia de execução?
  ↓
Runtime Engine           → Executa e devolve o resultado
```

Esta cadeia está materializada em **fases de desenvolvimento** e, depois da consolidação do Kernel, em **ramos de desenvolvimento** (A–F).

---

## 3. ÍNDICE DAS FASES E ESTADO ACTUAL

| Doc | Fase | Subsistema | Estado |
|---|---|---|---|
| `01-fase-0-...` | Fase 0 — Fundação e Governação | projecto + `.opencode` + docs | IMPLEMENTADA |
| `02-fase-1-...` | Fase 1 — Platform Foundation | `wsai2.platform` | IMPLEMENTADA |
| `03-fase-2-...` | Fase 2 — Hardware Intelligence | `wsai2.hardware` | IMPLEMENTADA |
| `04-fase-3-...` | Fase 3 — Runtime Intelligence | `wsai2.runtime` | IMPLEMENTADA |
| `05-fase-4-...` | Fase 4 — Capability Engine | `wsai2.capability` | IMPLEMENTADA |
| `06-fase-5-...` | Fase 5 — Model Intelligence | `wsai2.model` | IMPLEMENTADA |
| `07-fase-6-...` | Fase 6 — Provider Layer | `wsai2.provider` | IMPLEMENTADA |
| `08-fase-7-...` | Fase 7 — Task Intelligence | `wsai2.task` | IMPLEMENTADA |
| `09-fase-8-...` | Fase 8 — Runtime Engine | `core`, `execution`, `resource`, `security`, `extension`, `runtime_engine`, `infrastructure` | FECHADA (gate APPROVED WITH WARNINGS) |
| `10-fase-9-...` | Fase 9 — Knowledge Engine | `wsai2.knowledge` | FECHADA (âmbito lexical 9.1–9.7) |
| `11-fase-10-...` | Fase 10 — API | `wsai2.api` | API-01 CONCLUÍDA; API-02+ pendentes |
| `12-fase-11-...` | Fase 11 — UI | `wsai2.ui` (futuro) | NÃO INICIADA |
| `13-pos-kernel-...` | Pós-Kernel — Ramos A–F | Application, API, UI, Knowledge semântico, Addons, Projects | Ramo A em curso (APP-01..04 congeladas; APP-05 em implementação) |

---

## 4. MAPA DOS SUBSISTEMAS DE CÓDIGO

O pacote fonte `src/wsai2/` contém actualmente **17 subsistemas**:

```text
platform  hardware  runtime  capability  model  provider  task        (Fases 1–7)
core      extension  execution  resource  security  runtime_engine     (Fase 8)
infrastructure                                                         (Kernel, implementação pesada)
knowledge                                                             (Fase 9)
api                                                                    (Fase 10)
application                                                            (Ramo A)
```

`ui` é o único subsistema ainda **não antecipado** no código (marcado como futuro na fonte única de contratos).

---

## 5. A GRANDE SEPARAÇÃO CONCEPTUAL

Duas distinções atravessam todo o projecto e são centrais para o explicar:

1. **Hardware Capability ≠ Runtime State**
   O que a máquina *suporta* (estrutural) é diferente do que *está disponível agora* (momento a momento). Fases 2 e 3 materializam esta separação.

2. **Modelo ≠ Provider**
   O que quero executar (*Model Intelligence*, Fase 5) é diferente de como/onde posso executar (*Provider Layer*, Fase 6). Nenhum fornecedor ou modelo específico pode ser uma dependência do núcleo.

A estas soma-se a filosofia do **Core pequeno**: o núcleo contém contratos, entidades, invariantes e regras; as implementações pesadas vivem atrás dos contratos (Kernel), e as capacidades especializadas crescem como **addons** fora do núcleo.

---

## 6. GUIA PARA UTILIZAR ESTE RELATÓRIO NO NOTEBOOKLM

Cada documento desta pasta foi pensado para ser carregado de forma autónoma e para gerar vídeos explicativos de cada fase:

1. **Carregue um documento por vídeo** no NotebookLM (ou carregue o `00-visao-geral-e-indice.md` como contexto global de todos os vídeos).
2. **Use a secção "Ideias-chave para vídeo"** de cada documento como guião: contém os pontos que devem constar obrigatoriamente no vídeo.
3. **Comece pelo `00`** para ter o contexto da visão, e depois avance por cada fase (`01` → `12`).
4. **Roteiro recomendado de vídeos:**
   - Vídeo 0 — A visão e a arquitectura geral (doc 00);
   - Vídeos 1–8 — as fases 0–8, o núcleo funcional (docs 01–09);
   - Vídeo 9 — Knowledge Engine (doc 10);
   - Vídeo 10 — API (doc 11);
   - Vídeo 11 — UI (doc 12);
   - Vídeo 12 — o futuro pós-Kernel, ramos A–F (doc 13).
5. **Mantenha a linguagem**: "Hardware Intelligence", "Runtime Intelligence", "Capability Engine", "Model Intelligence", "Provider Layer", "Task Intelligence", "Runtime Engine", "Knowledge Engine" são os termos oficiais para usar no vídeo.

---

## 7. ESTRUTURA DOCUMENTAL ORIGINAL (FONTE DE VERDADE)

Este relatório é uma **tradução didáctica** do estado real do projecto. A fonte de verdade operacional continua a ser:

- `docs/project/PROJECT_STATE.md` — estado persistente;
- `docs/project/ROADMAP.md` — mapa macro das fases e ramos;
- `docs/project/IMPLEMENTATION_LOG.md` — registo detalhado de cada unidade;
- `docs/architecture/ARCHITECTURE.md` — a arquitectura;
- `docs/architecture/CONSTITUTION.md` — as regras arquitecturais;
- `docs/validation/` — relatórios formais de validação (Fase 8, Fase 9, Kernel);
- código real em `src/wsai2/` e testes em `tests/`.