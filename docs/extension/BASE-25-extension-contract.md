# WORKSTATION AI 2 — RELATÓRIO DA BASE: EXTENSION CONTRACT

## O que foi feito

Foi definido o **contrato mínimo declarativo para extensões (addons)** do
WorkStation AI 2: identidade, versão, versão do contrato, tipo funcional,
capacidades, dependências, recursos, permissões e estado de lifecycle.
É a unidade **Fase 8.1** do CORE_HARDENING_PLAN (hardening 01), a primeira
unidade implementável da **Fase 8 — Runtime Engine**.

Não foi implementada nenhuma lógica de execução, registo, gestão ou
scheduler. O contrato é puramente declarativo e imutável.

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8), etapa 8.1 "contratos mínimos".
- Base declarativa sobre a qual o Runtime Manager (8.5), a governação de
  recursos (8.3) e a camada de security/policy (hardening 09) se integrarão
  em unidades posteriores.
- O contrato **não acopla** a unidade ao Capability Engine, Provider Layer
  ou Model Intelligence: as capacidades são referidas por identificador
  textual, de modo reversível (constituição, artigo 8 — crescimento
  controlado).

## Para que serve

- Declarar, de forma estável e validada, o que uma extensão é e exige,
  antes de qualquer registo ou execução.
- Servir de base ao ciclo de vida do CORE_HARDENING_PLAN (hardening 02):

```text
DISCOVERED → VALIDATED → REGISTERED → INITIALIZING → READY
                                      ↓
                                  RUNNING
                                      ↓
                             DEGRADED / FAILED
                                      ↓
                              STOPPING → STOPPED
```

- Alinhar os tipos de extensão com as futuras políticas de segurança
  (hardening 09): analyst, code, agent, github_tool, mcp, utility.

## Ficheiros criados/alterados

- `src/wsai2/extension/base.py` — `ExtensionKind`, `ExtensionLifecycleState`,
  `ResourceLimit`, `ExtensionContract` (frozen, validado em `__post_init__`)
- `src/wsai2/extension/__init__.py` — exports públicos do submódulo
- `tests/test_extension.py` — 12 testes do contrato
- `docs/extension/BASE-25-extension-contract.md` — este relatório

Nenhum módulo existente das Fases 1–7 foi alterado.

## Dependências

- `base.py`: apenas stdlib (`dataclasses`, `enum`).
- Direcção das dependências: `extension` é um módulo folha — depende de
  nada do domínio e é consumido por unidades posteriores da Fase 8.
- Sem dependências de Runtime/Provider/Capability/Model (constituição,
  artigo 2 — dependências apontam para dentro).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **221 testes aprovados** (12 extension + 39 task + 46 provider
+ 42 model + 33 capability + 24 runtime + 17 hardware + 3 fundação + 5
platform). Regressão das 209 bases intacta.

Os testes validam:

- construção de contrato completo (todos os campos);
- defaults aplicados (capacidades, dependências, recursos, permissões,
  lifecycle `DISCOVERED`);
- imutabilidade (`frozen`);
- validação de `id`/`name`/`version`/`contract_version`/`kind` vazios →
  erro;
- enums de tipo e de lifecycle com os estados previstos;
- resumo textual do contrato e do limite de recurso.

## Estado da fase

**Fase 8 — Runtime Engine — EM CURSO**.

Etapa concluída:

- 8.0 baseline e auditoria ✓ (relatório `WSAI 2 — AUDITORIA`)
- 8.1 contratos mínimos — Extension Contract ✓ (esta unidade)

Em falta (unidades posteriores): Execution Context + Error Model (8.2),
Resource Governance (8.3), timeout/cancellation/recovery (8.4),
Runtime Manager + scheduler (8.5), lifecycle + compatibilidade (8.6),
testes de contrato arquitectural (8.7).

## Riscos residuais

- O `ResourceLimit` é declarativo; a governação efectiva de recursos é
  responsabilidade da Fase 8.3.
- `ExtensionKind` é uma lista aberta de categorias conhecidas, não fechada;
  poderá evoluir em unidades posteriores sem mudança de contrato.
- Não existe ainda validação de contratos de extensão (2 extensões com a
  mesma identidade, compatibilidade de versões) — responsabilidade da 8.6.

## Próximo passo

Fase 8.2 — **Execution Context + Error Model**: transporte consistente de
`execution_id`, `task_id`, `project_id`, deadline, cancellation token,
resource budget e prioridade, e a taxonomia de erros transversal
(Validation, Timeout, Cancellation, Resource, Execution).