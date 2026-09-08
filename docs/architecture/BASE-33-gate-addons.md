# WORKSTATION AI 2 — RELATÓRIO DO GATE: CORE PRONTO PARA ADDONS

## O que foi feito

Foi formalizada a unidade **Fase 8.9 — Gate — Core pronto para
addons**. O Gate **não é um novo módulo**: é a materialização do marco
do CORE_HARDENING_PLAN que precede qualquer addon de grande impacto
(code, agent, github_tool, mcp). Esta base documental regista o critério
executável e as duas integrações decididas na auditoria da 8.9:

1. **Propagação e contrato de composição da política** — o
   `Scheduler.run` passa a aceitar `policy: PolicyEngine | None = None`
   e a propagá-la ao `RuntimeManager` (a autorização aplica-se a cada
   plano **antes do passo 1**, junto da fila de agendamento). É o novo
   ponto de instituição junto da fila; quem cria o runtime fornece o
   motor real.
2. **Ponte `permissions` → `PolicyEngine`** — o `ExtensionRegistry
   .register` passa a aceitar `policy` (opt-in) e, registada a extensão,
   **concede as permissões declaradas como acções exactas ao principal =
   id da extensão**. Sem `policy`, o registo não muda nada.

Ambém foi criado o artefacto que faltava na auditoria: `tests/
test_gate_addons.py`, a **fotografia executável do Gate**.

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine (3.8):** fecha o marco de pré-requisitos do
  CORE_HARDENING_PLAN (hardening 01–11). Todos os pré-requisitos têm
  cobertura de testes; o Gate torna esse facto verificável.
- **`wsai2.security` permanece folha** (Artigo 2): ainda não depende de
  `extension`. A ponte vive no lado do registo (de `extension` para
  `security`), numa aresta nova autorizada em `FRONTEIRAS`:
  (`extension`, `security`).
- **Contrato de composição (documentado):** quem constrói o runtime
  (Manager/Scheduler) fornece o motor de política. Convenção de
  identidade: *quem executa trabalho de uma extensão leva
  `principal` = `id` da extensão* no `ExecutionContext`.

## Para que serve

- **Autorizar na fila, não só no gestor:** com esta unidade, um plano
  agendado é autorizado antes do primeiro passo — sem saltar a política.
- **Ligar o contrato à segurança:** `permissions` deixa de ser
  vocabulário morto; cada permissão declarada é uma **acção exacta**
  (negação por omissão) concedida à extensão que a declara.
- **Dar ao Gate um critério executável:** se `tests/test_gate_addons.py`
  falhar, a base deixou de satisfazer o critério do Gate — voltar à
  auditoria antes de declarar addons prontos.

## Regras registadas (decisões da auditoria 8.9)

1. **Contrato de composição, não bootstrap antecipado** — sem processo
   de produção ainda definido, a instituição real fica no contrato (o
   criador do runtime passa o motor); nenhum módulo novo é criado
   (Artigo 8).
2. **Exact-match por identidade de extensão** — a ponte concede cada
   string de `permissions` como acção ao `principal = id` da extensão;
   é o mesmo exact-match da 8.8, sem RBAC nem wildcard.
3. **Ponte no registo, no acto do registo** — `register(contrato, *,
   policy=None)`: após a transição para `REGISTERED` e apenas se
   `permissions` não estiver vazio; registar não é autorizar (o catálogo
   e a política são entidades distintas).
4. **Propagação no scheduler, aditiva** — `Scheduler.run(..., policy=
   PolicyEngine | None = None)`; sem motor, o comportamento 8.5 é
   preservado (regressão intacta).

## Ficheiros criados/alterados

- `src/wsai2/runtime_engine/scheduler.py` — kwarg `policy` + forwarding
- `src/wsai2/extension/registry.py` — kwarg `policy` + grants por id
- `tests/test_architecture_contract.py` — `FRONTEIRAS` + (`extension`,
  `security`)
- `tests/test_gate_addons.py` — critério executável do Gate (7 testes)
- `tests/test_extension_registry.py` — 3 testes da ponte (`permissions`
  → grants; sem policy invariante; registo independente da política)
- `tests/test_runtime_engine.py` — mocks do scheduler actualizados para
  o novo kwarg `policy`
- `docs/architecture/BASE-33-gate-addons.md` — este relatório

## Dependências

- `extension → security` (**nova**, autorizada em FRONTEIRAS): o registo
  usa `PolicyEngine` para materializar grants. `security` continua folha
  (não importa `extension`) — sem ciclos.
- `runtime_engine → security` (já existente): o scheduler propaga o motor.
- Nenhuma dependência nova introduzida em `core`/`resource`/`execution`.

## Testes

```text
py -3.12 -m pytest      →   397 passed
```

(387 bases anteriores + 10 desta unidade: 7 do Gate + 3 da ponte no
registo.) Cobertura do critério do Gate: pré-requisitos públicos;
propagação da política no scheduler com execução autorizada e com
negação antes do passo 1 (passos `SKIPPED`, `PermissionError`
`wsai.permission`); agendamento sem política preservado; ponte por
identidade de extensão; negação por omissão sem grants; isolamento de
projectos taxonómico. Regressão 100% intacta — alteração aditiva e
reversível.

## Estado da fase

Fase 8 — Runtime Engine: **Gate — Core pronto para addons APROVADO**
(clarificado pela 8.9). Concorrência entre planos, filas multicamadas e
monitorização contínua permanecem **unidades posteriores** da Fase 8
(barra de progresso mantém 95%); o Gate garante os pré-requisitos de
addons, não a totalidade das capacidades de produção do Runtime.

## Riscos residuais

- A política continua **injectada**: no bootstrap real, o ponto que
  constrói o runtime deve passar o motor e garantir que planos de
  extensões levam `principal = id` da extensão. Enquanto isso não
  acontecer, o enforcement não é activo por omissão (regalienado por
  decisão da 8.8 — sem regressão).
- `permissions` é um vocabulário aberto; se um addon inventar strings,
  não executará (exact-match) — comportamento seguro, mas a política de
  grants de cada addon real é definida quando os addons chegarem.

## Próximo passo

Após o Gate, a Fase 8 tem **unidades residuais opcionais** (concorrência
entre planos, filas multicamadas, monitorização contínua) e a **Fase 9 —
Knowledge Engine** pode arrancar. Decisão a registar no `PROJECT_STATE`:
seguir com a Fase 9 ou fechar os residuais de produção do Runtime antes.