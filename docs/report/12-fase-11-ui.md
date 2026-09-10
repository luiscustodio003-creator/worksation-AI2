# WORKSTATION AI 2 — RELATÓRIO DA FASE 11

## UI (INTERFACE DE UTILIZADOR)

**Subsistema:** `wsai2.ui` (futuro)
**Referência arquitectural:** subsistema 3.11
**Roadmap:** Fase 11
**Estado actual:** NÃO INICIADA — ainda marcada como subsistema futuro na fonte única de contratos (`SUBSISTEMAS_FUTUROS = ("ui",)`)

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

A inteligência do WSAI 2 existe para servir o utilizador. A Fase 11 resolve o último elo: **apresentar informação real e operações disponíveis**, de forma compreensível, sem conter a lógica central de decisão.

> "A interface apresenta capacidades reais e consome contratos da aplicação." (Constituição, artigo 7)

A UI é **consumidora** — apresenta o que o sistema realmente produz através da Application/API, nunca fabrica dados nem decide por si.

## 2. O QUE ESTÁ PLANEADO (ROADMAP)

```text
UI-01  Application Shell
UI-02  Dashboard
UI-03  Hardware
UI-04  Models
UI-05  Capabilities
UI-06  Tasks
UI-07  Runtime
UI-08  Knowledge
UI-09  Execution / Status
UI-10  UI Integration Gate
```

Cada área corresponde a uma superfície real do núcleo: o utilizador vê o perfil de hardware, o estado de runtime, as capacidades disponíveis, os modelos, as tarefas, o conhecimento e o estado das execuções.

## 3. PORQUE AINDA NÃO FOI INICIADA

O desenvolvimento é controlado por dependências (Constituição, artigo 8 — não antecipar):

```text
APPLICATION (Ramo A) ───► API (Ramo B) ───► UI (Ramo C)
```

A UI só faz sentido **depois** de existirem os contratos de use-case (Application) e de a API os expor. Antes disso, criar a interface seria construir sobre areia. A regra visa exactamente isto: "não criar módulos, abstrações ou ficheiros sem necessidade demonstrada pela fase actual".

## 4. CONEXÃO COM A VISÃO

>A visão termina com o utilizador a poder dizer simplesmente: "quero fazer isto". O sistema fará a análise, selecção, preparação e execução; e "quando não for possível decidir automaticamente, deverá explicar a razão e apresentar alternativas."

É na Fase 11 que essa experiência se materializa: o utilizador deixa de pensar em modelos, threads, backends e memória — vê o que o sistema recomenda e porque, e interage apenas com a tarefa.

## 5. ESTADO E PRÓXIMOS PASSOS

- **Estado:** não iniciada; subsistema futuro na fonte única.
- **Pré-requisitos:** concluir o Ramo A (Application) e avançar o Ramo B (API).
- **Decisões materiais futuras:** tecnologia da interface (a visão não a fixa), experiência do dashboard, forma de apresentar justificações de decisão e alternativas.
- **Regra para o vídeo:** explicar a UI como **camada de apresentação**, não como núcleo — o oposto da arquitectura das aplicações tradicionais.

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: apresentar ao utilizador as capacidades reais do sistema de forma clara.
2. Solução (planeada): UI com dashboard, hardware, modelos, capacidades, tarefas, runtime, conhecimento e execução.
3. Ideia central: a UI **apresenta** e **consome contratos**; não contém lógica de negócio (artigo 7).
4. Porque ainda não começou: dependências — primeiro os contratos de use-case (Application), depois a API, só então a UI.
5. Visão final: o utilizador diz "quero fazer isto"; o sistema decide, explica e executa — e a UI mostra essa inteligência.