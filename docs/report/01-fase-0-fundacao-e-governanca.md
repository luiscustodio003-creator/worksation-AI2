# WORKSTATION AI 2 — RELATÓRIO DA FASE 0

## FUNDAÇÃO E GOVERNAÇÃO

**Subsistema:** projecto `wsai2` + governação OpenCode (`/wsai-run`, skills, políticas)
**Referência arquitectural:** pré-requisito de todas as camadas
**Roadmap:** Fase 0
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

A Fase 0 estabelece a infra-estrutura mínima e as **regras do jogo** que vão governar todo o desenvolvimento futuro. Sem ela, cada módulo nasceria com convenções diferentes, sem testes e sem forma de saber o estado real do projecto.

Esta fase responde a três perguntas:

1. **Como se instala e se testa o projecto?** — estrutura Python mínima (`pyproject.toml`, pacote `wsai2`, base de testes).
2. **Quais são as regras de arquitectura e de desenvolvimento?** — Constituição, Arquitectura, Roadmap, estado persistente.
3. **Como um agente de IA desenvolve o projecto de forma controlada?** — comandos `/wsai-run` e família `/wsai-*`, skill de desenvolvimento, políticas de modelos e de Git.

É a fase que torna todo o resto **verificável** e **governado**.

## 2. ARQUITECTURA DA FASE

```text
README.md  AGENTS.md  CONSTITUTION.md  ARCHITECTURE.md  ROADMAP.md
          PROJECT_STATE.md  IMPLEMENTATION_LOG.md  RUN_GOVERNANCE.md
                      .opencode/commands/wsai-*.md
                      .opencode/skills/wsai-development/SKILL.md
                      pyproject.toml  src/wsai2/  tests/
```

### O ciclo de desenvolvimento controlado

```text
AUDITAR → PLANEAR → ARQUITECTURAR → IMPLEMENTAR → TESTAR → VALIDAR → DOCUMENTAR → GIT → FREEZE
```

Cada unidade de trabalho passa por este ciclo. Quando uma unidade termina, o estado é persistido e a próxima unidade é determinada.

## 3. COMPONENTES PRINCIPAIS

- **`README.md`** — visão geral pública do projecto.
- **`AGENTS.md`** — regras globais que todos os agentes seguem.
- **`docs/architecture/CONSTITUTION.md`** — os 13 artigos arquitecturais (responsabilidade dos módulos, dependências para dentro, isolamento de SO, separação hardware/runtime, API/UI como camadas finais, crescimento controlado, testabilidade, documentação, independência de modelos/fornecedores, etc.).
- **`docs/architecture/ARCHITECTURE.md`** — camadas e subsistemas funcionais (3.1–3.11).
- **`docs/project/ROADMAP.md`** — as 12 fases e os ramos pós-Kernel.
- **`docs/project/PROJECT_STATE.md`** — o estado persistente (a fonte de verdade operacional).
- **`docs/project/IMPLEMENTATION_LOG.md`** — o registo de cada unidade concluída.
- **Comando `/wsai-run`** — orquestrador que trabalha por ramos e unidades.
- **Skill `wsai-development`** — guião do desenvolvimento assistido.

## 4. CONEXÃO COM A VISÃO

>A visão exige um sistema que cresce por camadas sem se tornar monolítico, com regras claras e um núcleo pequeno e previsível. A Fase 0 fixa as regras que tornam essa visão possível de construir de forma incremental e verificável.

A Fase 0 é a base documental e de governação — **não implementa nenhum subsistema funcional**. É deliberadamente leve: nada é criado sem necessidade demonstrada (Constituição, artigo 8).

## 5. EVIDÊNCIA E VALIDAÇÃO

- Base de testes inicial a funcionar: `py -3.12 -m pytest` → **3 passed** no arranque.
- Ficheiros de governação criados e sincronizados no repositório remoto oficial.
- Os testes de contrato arquitectural (da Fase 8.7) verificam até hoje que a estrutura respeita as regras definidas aqui (artigos 1, 2, 4, 8, 9, 10).

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Sem governação, um projecto como o WSAI 2 tornar-se-ia monolítico e não verificável.
2. A Fase 0 fixa as regras: Constituição (13 artigos), Arquitectura, Roadmap e estado persistente.
3. O desenvolvimento é incremental e controlado: cada unidade passa por AUDITAR → IMPLEMENTAR → TESTAR → DOCUMENTAR → GIT.
4. A regra de ouro do crescimento: "não criar módulos sem necessidade demonstrada" (artigo 8).
5. É uma fase de fundação — ainda não há inteligência funcional, apenas o "tabela de leis" e o "altifalante" de verificação.