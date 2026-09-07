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
- A interface apresenta informação real produzida pelos serviços internos.
- Cada alteração relevante deve incluir testes e documentação.
- O desenvolvimento é incremental e controlado por fases.
- Cada base concluída produz um relatório de validação.
- O estado do projecto é persistido em `docs/project/PROJECT_STATE.md`.

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

Antes de iniciar trabalho novo, o processo deve inspeccionar o estado do projecto, a arquitectura, os testes e a sincronização Git.

## Estado actual

**Fase 0 — Fundação Arquitectural e Governação do Desenvolvimento**

Consultar:

`docs/project/PROJECT_STATE.md`

## Sincronização

O repositório remoto oficial é:

https://github.com/luiscustodio003-creator/worksation-AI2

O directório aberto no VS Code é a cópia de trabalho local. Todas as alterações devem ser verificadas, testadas, documentadas e versionadas através de Git antes de serem consideradas concluídas.
