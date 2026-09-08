# WORKSTATION AI 2 — RELATÓRIO DA BASE: SECURITY / POLICY + PROJECT ISOLATION

## O que foi feito

Foi implementada a unidade **Fase 8.8 — Security/Policy + Project
Isolation** (hardening 09 e 10 do CORE_HARDENING_PLAN), pré-requisito do
**Gate — Core pronto para addons**. Novo subsistema folha
**`wsai2.security`** com:

- `base.py` — tipos puros: `Principal` (id, projecto, permissões) e
  `PolicyDecision` (acção, principal, projecto, veredicto, justificação);
- `policy.py` — `PolicyEngine` que decide **exact-match por acção**
  (a acção é concedida se e só se está declarada nas permissões) e
  `denied_decision` (converte a negação no `PermissionError` da 8.2);
- `isolation.py` — guardas de fronteira de projecto (`require_project`,
  `assert_same_project`) com emissão do `ProjectIsolationError` da 8.2.

Integração mínima no Runtime Engine: o `RuntimeManager.execute_plan`
aceita um `policy` opcional e aplica a decisão **antes do passo 1**;
negada, devolve `ExecutionReport` `FAILED` com `PermissionError` (passos
`SKIPPED`) sem executar qualquer runner.

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8): fecha os hardening 09 e
  10 do CORE_HARDENING_PLAN, últimos pré-requisitos do Gate de addons.
- `wsai2.security` é **folha** (Artigo 2): depende apenas de `wsai2.core`
  (erros e contexto). Não conhece extensões, fornecedores nem modelos —
  a política recebe strings opacas e devolve decisões.
- As `FRONTEIRAS` do contrato arquitectural (8.7) cresceram com
  (`security`, `core`) e (`runtime_engine`, `security`) — verificadas
  pelos próprios contract tests.
- Artigo 12 (análise de impacto): este relatório documenta o impacto da
  alteração; o `ExecutionContext` (8.2) recebeu **um campo aditivo**
  (`principal`, default `""`) sem quebrar qualquer construtor existente.

## Para que serve

- **Autorizar antes de executar:** com o Gate de addons, nenhuma extensão
  de alto impacto (code, github_tool, agent, mcp) deverá executar sem uma
  política que conceda a acção `execute` ao principal no seu projecto.
- **Activar a taxonomia morta da 8.2:** `PermissionError` e
  `ProjectIsolationError` passam a ter emissores reais no repositório.
- **Isolar projectos (hardening 10):** a fronteira exige `project_id` e
  impede acesso cruzado entre projectos, propagando o erro taxonómico.
- **Manter o núcleo desacoplado:** sem política fornecida, o gestor
  comporta-se exactamente como antes (nenhuma regressão; a governação de
  recursos da 8.3 e as políticas da 8.4 ficam intactas).

## Regras registadas (decisões da auditoria 8.8)

1. **Uma unidade para 09+10** — subsistema único `wsai2.security`, mínimo
   para o Gate (sem RBAC, sem hierarquias, sem wildcard).
2. **Exact-match por acção** — a cadeia é
   `principal -> project -> action -> policy -> decision`; negação por
   omissão (catálogo vazio/desconhecido → não concedido).
3. **Enforcement antes do passo 1** — no `RuntimeManager.execute_plan`,
   após as validações de plano/contexto e antes da primeira chamada do
   `step_runner`; negação = relatório `FAILED` + `PermissionError`, sem
   executar passos (observável e testável).
4. **Principal opcional no contexto** — `ExecutionContext.principal`
   (default `""`) é aditivo; só é exigido quando uma política é fornecida
   (aí, principal/projecto vazios → `ValidationError` de configuração).
5. **Policy injectada** — sem motor fornecido, `execute_plan` não aplica
   autorização (comportamento 8.5/8.7 preservado); o Runtime deve
   decidir onde instalar a política no Gate.

## Ficheiros criados/alterados

- `src/wsai2/security/base.py` — `Principal`, `PolicyDecision`
- `src/wsai2/security/policy.py` — `PolicyEngine`, `denied_decision`
- `src/wsai2/security/isolation.py` — `require_project`, `assert_same_project`
- `src/wsai2/security/__init__.py` — exports públicos
- `src/wsai2/core/context.py` — campo aditivo `principal` (default `""`)
- `src/wsai2/runtime_engine/manager.py` — `policy` opcional no `execute_plan`
- `tests/test_security_policy.py` — 11 testes
- `tests/test_security_isolation.py` — 6 testes
- `tests/test_security_integration.py` — 6 testes
- `tests/test_architecture_contract.py` — `FRONTEIRAS` +2 arestas
- `docs/security/BASE-32-security-policy-isolation.md` — este relatório

## Dependências

- `security` → `wsai2.core` (errors, context) apenas.
- `runtime_engine` → `wsai2.security` (folha) — sem ciclo: `security` não
  importa `runtime_engine`.
- A `core/context.py` continua a referenciar `ResourceLimit` apenas em
  `TYPE_CHECKING` (sem dependência de runtime em `extension`).

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **387 testes aprovados** (23 novos desta unidade + 364 bases
anteriores). Regressão intacta — alteração 100% aditiva.

Cobertura dos 23 novos testes:

- **policy (11):** concessão exacta; sensibilidade a maiúsculas; acção não
  declarada → negação; principal desconhecido → negação; principal/projecto
  vazios → `ValidationError` (`wsai.security.principal`/`.project`);
  `grant` acumulativo; `decide_principal`; decisão imutável; conversão em
  `PermissionError` (detalhes de acção/principal/projecto); resumo textual.
- **isolation (6):** `require_project` validar/normalizar/rejeitar;
  mesmo projecto passa; projectos diferentes →
  `ProjectIsolationError` com esperado/actual em `details`.
- **integração (6):** plano autorizado executa (3 passos SUCCESS); plano
  não autorizado → `FAILED` + `PermissionError`, passos `SKIPPED`, runner
  nunca chamado; principal/projecto em falta com policy → erro de
  configuração; contexto omisso sem policy → regressão preservada;
  emissor de `ProjectIsolationError` no relatório.

## Estado da fase

Fase 8 — Runtime Engine: **8.8 concluída** (8.1–8.8). Com os hardening
09 e 10 implementados (núcleo), o **Gate — Core pronto para addons** é
o próximo marco formal. Concorrência entre planos, filas multicamadas e
monitorização contínua permanecem para unidades posteriores da Fase 8.

## Riscos residuais

- A política é declarativa e injectada: **quem fornece o motor de
  política no Gate é responsabilidade da integração** (configuração real
  do Runtime), ainda não decidida.
- `permissions` do `ExtensionContract` (8.1) continuam um vocabulário
  declarativo; ligá-las aos grants do `PolicyEngine` é integração
  posterior de arranque de addons (não anunciada).
- A hierarquia/wildcard foram deliberadamente recusados (exact-match);
  uma semântica mais permissiva exigiria revisão de contrato.

## Próximo passo

**Gate — Core pronto para addons** (formalização): executar a base de
validação completa, confirmar os pré-requisitos (contratos, lifecycle,
recursos, cancelamento, compatibilidade, segurança, isolamento — todos
com cobertura de testes), e decidir onde a política real é instituída e
como `permissions` da extensão alimentam o `PolicyEngine`. Concorrência
e monitorização são unidades posteriores da Fase 8; a Fase 9 (Knowledge
Engine) arranca depois do Gate.