# WorkStation AI 2

## Visão geral

O **WorkStation AI 2 (WSAI 2)** é uma plataforma local e multiplataforma de inteligência artificial concebida para analisar os recursos reais do computador e seleccionar, planear e executar as capacidades de IA mais adequadas.

O projecto é desenvolvido de forma incremental, modular e orientada por arquitectura.

## Objectivo

O WSAI 2 deverá funcionar em Windows e Linux e evoluir através de subsistemas claramente separados:

1. Platform Foundation
2. Hardware Intelligence
3. Runtime Intelligence
4. Capability Engine
5. Model Intelligence
6. Provider Layer
7. Task Intelligence
8. Runtime Engine
9. Knowledge Engine
10. API
11. Interface de utilizador

## Princípios fundamentais

- Uma responsabilidade principal por módulo.
- O núcleo do domínio não depende da interface, API ou fornecedor externo.
- Hardware Capability e Runtime State são conceitos separados.
- Model Intelligence e Provider Layer são responsabilidades distintas.
- A interface apresenta informação real produzida pelos serviços internos.
- Cada alteração relevante deve incluir testes e documentação.
- O desenvolvimento é incremental e controlado por fases.
- Cada base concluída produz um relatório de validação.
- O estado do projecto é persistido em `docs/project/PROJECT_STATE.md`.

## Provider Layer

O Provider Layer é agnóstico a fornecedor. O catálogo actual inclui **Ollama**, **llama.cpp** através do protocolo compatível com OpenAI e um adaptador genérico para APIs compatíveis com OpenAI.

A camada já possui contratos, registo, detecção, adaptadores de runtime e health checks. O código separa a lógica de decisão do I/O externo através de interfaces e transportes injectáveis.

A integração actual valida os protocolos através de testes e servidores locais controlados. A presença de uma instalação concreta de Ollama ou llama.cpp na máquina do utilizador deve ser verificada em runtime; não é assumida pelo catálogo.

## Desenvolvimento

O desenvolvimento assistido é governado por:

- `.opencode/commands/wsai-run.md`
- `.opencode/skills/wsai-development/SKILL.md`
- `AGENTS.md`
- documentação arquitectural
- estado persistente do projecto

O comando principal é:

```text
/wsai-run
```

Durante a execução, o agente deve manter progresso visível no fluxo da execução, indicando fase, unidade, etapa, estado e próximo passo, sem gerar ruído por cada comando trivial.

Antes de iniciar trabalho novo, o processo deve inspeccionar o estado do projecto, a arquitectura, os testes e a sincronização Git.

## Estado actual

A **Fase 8 — Runtime Engine** está **formalmente concluída**: unidades 8.1–8.9 e os três residuais Via B (monitorização contínua, concorrência entre planos e filas multicamadas) implementados, com o gate de fundação **APPROVED WITH WARNINGS** e relatório persistente em `docs/validation/FOUNDATION_VALIDATION_REPORT.md`.

A **Fase 9 — Knowledge Engine** está **em curso**. A unidade 9.1 (contrato declarativo do subsistema 3.9 — `wsai2.knowledge`) está concluída; as unidades seguintes (ingestão/admissão, extracção, metadados, indexação, recuperação e contexto) são governadas pelo `PROJECT_STATE.md`.

O estado persistente e a fonte de verdade operacional encontram-se em:

`docs/project/PROJECT_STATE.md`

O estado persistente regista a Fase 8 formalmente fechada e o início da Fase 9 (unidade 9.1 — contrato do Knowledge Engine concluída).

## Sincronização

O repositório remoto oficial é:

https://github.com/luiscustodio003-creator/worksation-AI2

O directório aberto no VS Code é a cópia de trabalho local. Todas as alterações devem ser verificadas, testadas, documentadas e versionadas através de Git antes de serem consideradas concluídas.
