# WSAI 2 — FOUNDATION READINESS AUDIT

## Data

2026-09-08

## Commit de referência da auditoria

`41d92d4cc26eaa85c57537cd7425237affb79290` — último estado funcional antes das correcções desta auditoria.

## Objectivo

Comparar o estado real do repositório com `PROJECT_STATE.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `CORE_HARDENING_PLAN.md`, comandos OpenCode e skill de desenvolvimento, procurando lacunas funcionais, inconsistências de governação e evidência de testes insuficiente.

## Resultado executivo

**Estado: 🟡 APPROVED WITH WARNINGS para continuidade controlada da Fase 8.**

A arquitectura base está coerente com a evolução registada: os subsistemas principais existem, a Fase 8.1–8.9 e os residuais 1–2 estão documentados, e o `Scheduler`/`RuntimeManager`/`ResourceGovernor` implementam os contratos descritos. O estado remoto confirmou a existência das fronteiras `core`, `hardware`, `runtime`, `capability`, `model`, `provider`, `task`, `execution`, `runtime_engine`, `resource`, `extension` e `security`.

Não foi encontrada razão para reescrever ou duplicar os subsistemas existentes.

## Matriz de auditoria

| Área | Estado | Evidência | Acção |
|---|---|---|---|
| Platform Foundation | IMPLEMENTADO | `src/wsai2/platform` + estado persistente | manter |
| Hardware Intelligence | IMPLEMENTADO | `src/wsai2/hardware` | manter |
| Runtime Intelligence | IMPLEMENTADO | `src/wsai2/runtime` | manter |
| Capability Engine | IMPLEMENTADO | `src/wsai2/capability` | manter |
| Model Intelligence | IMPLEMENTADO | `src/wsai2/model` | manter |
| Provider Layer | IMPLEMENTADO | `src/wsai2/provider` | manter |
| Task Intelligence | IMPLEMENTADO | `src/wsai2/task` | manter |
| Execution Context / Error Model | IMPLEMENTADO | `src/wsai2/core` + hardening 03/04 | manter |
| Resource Governance | IMPLEMENTADO | `src/wsai2/resource` + hardening 05 | manter |
| Execution Policies | IMPLEMENTADO | `src/wsai2/execution` + hardening 06 | manter |
| Runtime Manager / Scheduler | IMPLEMENTADO | `src/wsai2/runtime_engine` + hardening 07 | manter |
| Monitoring | IMPLEMENTADO | `wsai2.runtime_engine.monitoring` + BASE-34 | manter |
| Concurrency | IMPLEMENTADO | `Scheduler.run(concurrency=...)` + BASE-35 | manter |
| Multilayer queues | AUSENTE / PRÓXIMA UNIDADE | PROJECT_STATE | implementar apenas após novo audit/plan |
| Extension lifecycle / compatibility | IMPLEMENTADO | `src/wsai2/extension` + hardening 02/08 | manter |
| Security / Policy | IMPLEMENTADO | `src/wsai2/security` + hardening 09 | manter |
| Project isolation | IMPLEMENTADO | `wsai2.security.isolation` + hardening 10 | manter |
| Architecture contract tests | IMPLEMENTADO | `tests/test_architecture_contract.py` | manter/evoluir |
| Addons gate | IMPLEMENTADO | `tests/test_gate_addons.py` | manter |
| `/wsai-validate` | IMPLEMENTADO | `.opencode/commands/wsai-validate.md` | integrar em todos os contratos |
| Skill | PARCIALMENTE ALINHADA | faltava explicitar validate e precedência do código real | corrigido |
| PROJECT_STATE | INCONSISTENTE | família de comandos omitia `/wsai-validate` | corrigido |
| Gate negative test | FRÁGIL | runner era definido mas não injectado | corrigido |
| CI GitHub Actions | AUSENTE | `.github/workflows` não encontrado | P2, não bloqueia a arquitectura local |

## Correcções efectuadas

### 1. Teste negativo do Gate

`tests/test_gate_addons.py` definia um `runner` que não era passado ao `Scheduler`. A asserção de que nenhum passo tinha sido executado era, portanto, fraca: o teste verificava `executado == []`, mas o runner nunca poderia ser chamado.

Correcção: injectar `step_runner=runner` no cenário de negação. Assim, a mesma asserção passa a observar efectivamente o comportamento que o teste pretende garantir: a política nega antes do passo 1.

### 2. PROJECT_STATE

A lista oficial de comandos foi actualizada para incluir `/wsai-validate`, e os papéis de todos os comandos foram explicitados. O estado também passou a distinguir baseline anterior da nova validação local necessária.

### 3. Skill `wsai-development`

A skill foi alinhada com a arquitectura actual e passou a estabelecer explicitamente:

- precedência do código/testes sobre documentação desactualizada;
- família oficial de comandos incluindo `/wsai-validate`;
- auditoria de responsabilidades existentes antes de criar novos módulos;
- distinção entre teste normal e gate de consolidação;
- obrigação de considerar a qualidade comportamental dos testes;
- ciclo `AUDIT → PLAN → IMPLEMENT → TEST → VALIDATE → DOC → GIT`;
- paragem quando um gate ou decisão arquitectural material impedir progressão segura.

## Comandos

`/wsai-run` já estava alinhado com a composição do ciclo e já referenciava `/wsai-validate`. `/wsai-audit` e `/wsai-plan` também respeitam a regra de não duplicação e de planeamento antes da implementação.

O principal desalinhamento encontrado era documental: `PROJECT_STATE.md` não listava `/wsai-validate`, apesar de o comando existir e de `/wsai-run` já o utilizar como gate.

## Segurança da evolução

Não foram identificadas razões para criar uma segunda arquitectura, substituir `Scheduler`, `RuntimeManager`, `ResourceGovernor` ou duplicar Capability/Provider/Task registries. A evolução deve permanecer aditiva.

A próxima unidade continua a ser **Filas multicamadas**, mas permanece uma unidade material da Fase 8 e deve passar pelo ciclo controlado antes da implementação.

## Limitações da auditoria remota

Esta auditoria confirmou estrutura, contratos, código relevante, documentação e testes existentes no GitHub. A execução dos 415+ testes requer o ambiente local Python/pytest; por isso, a correcção do teste do Gate foi submetida mas a baseline final pós-correcção deve ser confirmada localmente antes de declarar uma nova contagem.

A ausência de `.github/workflows` significa que não existe evidência de CI GitHub Actions neste estado. Isto é uma lacuna de automação (P2), não uma razão para alterar a arquitectura funcional agora.

## Decisão

**Não reestruturar o Core. Não iniciar Knowledge/API/UI.**

Primeiro:

1. confirmar localmente a suíte após a correcção do Gate;
2. manter os comandos e a skill agora alinhados;
3. executar `/wsai-run` para a unidade de filas multicamadas apenas quando o ambiente local estiver sincronizado;
4. após concluir a Fase 8, executar `/wsai-validate foundation`;
5. só com `FOUNDATION APPROVED` avançar para a Fase 9.
