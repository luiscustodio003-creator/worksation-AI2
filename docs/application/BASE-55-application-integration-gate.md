# WORKSTATION AI 2 — BASE-55: APPLICATION INTEGRATION GATE (APP-11)

## Responsabilidade

Validar a coerência global do Ramo A (Application / Use-Case Boundary) e,
se aprovado, declarar o ramo `COMPLETE / FROZEN` — conforme a regra de
retoma do `RUN_STATE`.

## Critérios

1. **Suíte completa verde** (nenhuma regressão no Kernel nem nos domínios):
   `py -m pytest --tb=no` → **570 passed, 0 failures, 0 errors, 0 skipped**.
2. **Fronteira Application sancionada**: `FRONTEIRAS` contém as 9 arestas
   `application → {capability, core, hardware, knowledge, model, platform,
   runtime, runtime_engine, task}`; `FIREWALL["application"]` coincide
   exactamente com esse conjunto (não inclui `provider`).
3. **Superfície versionada**: `SUPERFICIES_PUBLICAS["application"]` ==
   `__all__` de `wsai2.application` (30 símbolos = 20 contratos + 10
   serviços); `APPLICATION_CONTRACT_VERSION == "1.0"` em `CONTRACT_VERSIONES`.
4. **Contratos → serviços 1:1**: cada par pedido/resposta de APP-02 tem o
   serviço correspondente (System, Hardware, Runtime, Capabilities, Models,
   Tasks, Knowledge, Execution, Status, Cancellation).
5. **Base documental completa**: `BASE-46` (contratos) e `BASE-47..54`
   (evidências das unidades APP-03..10); docstrings actuais em todos os
   módulos.
6. **Sem placeholders**: nenhum `TODO`/`NotImplementedError` nos módulos do
   ramo; serviços consumidos ao nível do pacote.

## Decisão

`APPROVED` — o Ramo A está coerente, testado e documentado.

```text
BRANCH A — APPLICATION / USE-CASE BOUNDARY: COMPLETE / FROZEN
Testes: 570/570 verdes
Gateway: PASSED
Próximo ramo: B — API (PENDING), primeira unidade API-02.
```

## Validação

```text
py -m pytest --tb=no
tests=570  failures=0  errors=0  skipped=0
```