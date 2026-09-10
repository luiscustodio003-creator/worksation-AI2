# WORKSTATION AI 2 — RELATÓRIO DA FASE 8

## RUNTIME ENGINE

**Subsistemas:** `wsai2.core`, `wsai2.extension`, `wsai2.execution`, `wsai2.resource`, `wsai2.security`, `wsai2.runtime_engine`, `wsai2.infrastructure`
**Referência arquitectural:** subsistema 3.8
**Roadmap:** Fase 8 (unidades 8.1–8.9 + 3 residuais Via B)
**Estado actual:** FECHADA — gate de validação da fundação **APPROVED WITH WARNINGS** (2026-09-09), relatório em `docs/validation/FOUNDATION_VALIDATION_REPORT.md`

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

Depois do Task Intelligence produzir o `ExecutionPlan`, alguém tem de o **executar de forma segura, governada e observável**.

> A Fase 8 resolve o problema de executar planos com recursos limitados, tempo limitado, cancelamento, concorrência e políticas de segurança — sem que os addons tenham de inventar mecanismos incompatíveis.

Não se trata de reinventar a inferência: trata-se de **governar a execução**. É a fase mais complexa do núcleo e fechou o "Core pronto para addons".

## 2. ARQUITECTURA DA FASE (AS UNIDADES)

A fase foi construída em unidades, seguindo o plano de hardening do Core:

```text
8.1  Extension Contract ......... contrato declarativo de addons
8.2  Execution Context + Erros .. taxonomia uniforme de erros + contexto de execução
8.3  Resource Governance ......... limites declarativos, avaliação e accounting
8.4  Execution Policies .......... timeout, cancelamento cooperativo, recuperação
8.5  Runtime Engine .............. gestor + scheduler que consomem o ExecutionPlan
8.6  Lifecycle + Compatibility ... máquina de estados de extensões + versioning
8.7  Architecture Contract Tests . regras da Constituição tornadas testes executáveis
8.8  Security / Policy + Isolação  PolicyEngine + fronteira de projectos
8.9  Gate — Core pronto p/ addons  critério executável para o ecossistema de addons
Via B: monitorização contínua, concorrência entre planos, filas multicamadas
```

### As peças que a compõem no código

- **`wsai2.core`** — erros (`WsaiError` com `code` estável, 10 categorias) e `ExecutionContext` imutável (deadline, cancelamento cooperativo, budget, prioridade, principal).
- **`wsai2.resource`** — `ResourceGovernor` (thread-safe): limites declarativos, `evaluate/allocate/release`, accounting por instância.
- **`wsai2.execution`** — políticas: timeout, `DeadlineGuard`, cancelamento por checkpoints, retry/recovery, `execute_with_policies`.
- **`wsai2.extension`** — contrato de addon, `ExtensionRegistry`, lifecycle puro (10 estados), `ContractVersion` (compatibilidade por `major`).
- **`wsai2.security`** — `PolicyEngine` (decisão exact-match por acção, negação por omissão), `require_project`/`assert_same_project`.
- **`wsai2.runtime_engine`** — `RuntimeManager`, `Scheduler` (sequencial por omissão, concorrência opcional), `ExecutionMonitor`, `MultilayerExecutionQueue`.
- **`wsai2.infrastructure`** — a implementação pesada (governor, manager, scheduler, filas, monitorização), em resultado da migração do Kernel.

## 3. AS GARANTIAS DA FASE

- **Timeout** pelo prazo mais curto; orçamento libertado em `finally`.
- **Cancelamento cooperativo** por token — a thread worker daemon nunca é morta à força.
- **Recuperação** por plano inteiro, com registo limpo por tentativa e retry opt-in.
- **Política** aplicada antes do passo 1: negação = plano FAILED com passos SKIPPED e runner não chamado.
- **Isolamento de falhas de addons** — o lifecycle é puro; uma falha de extensão não derruba o Core.
- **Determinismo** por omissão (agendamento sequencial estável por prioridade) com capacidade opcional de paralelismo e filas por prioridade com backlog e preempção apenas de trabalho pendente.

## 4. CONEXÃO COM A VISÃO

>A visão pede um Core pequeno, rápido e previsível: "queremos um núcleo pequeno, sólido e previsível sobre o qual possam crescer addons especializados" e "o Core deve definir as regras, contratos, entidades e invariantes".

A Fase 8 é onde essa filosofia se prova: contratos e invariantes no núcleo; implementação pesada atrás dos contratos (Kernel); extensões governadas por lifecycle, compatibilidade e política — sem tocar no núcleo. Com o Gate 8.9, o Core fica **pronto para o ecossistema de addons**.

## 5. EVIDÊNCIA E VALIDAÇÃO

- Gate da fundação: `tests=423, failures=0` no fecho da Fase 8; **APPROVED WITH WARNINGS** (avisos P3 não bloqueantes: FV-02 CI remota por confirmar; FV-04 ordem de prioridades duplicada como melhoria futura).
- 10/10 testes de contrato arquitectural; invariantes de concorrência, filas e monitorização validados.
- A migração do Kernel (KERNEL-01..10) consolidou depois esta fundação em `main`.

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: depois de planear, é preciso executar com segurança, limites e observação.
2. Solução: Runtime Engine — gestor, scheduler, governação de recursos, políticas de execução e segurança.
3. O plano é a unidade de políticas; o passo é a unidade de observação.
4. Extensões: lifecycle puro, compatibilidade por contrato, política antes do passo 1; uma falha de addon não derruba o Core.
5. Residuais Via B: monitorização contínua, concorrência opcional entre planos e filas multicamadas.
6. Fecho: Gate "Core pronto para addons" — a base para todo o pós-Kernel.