# WSAI 2 — PLANO DA UNIDADE 8.6: LIFECYCLE + COMPATIBILITY

## Objectivo

Fechar o hardening 02 (Lifecycle) e 08 (Versioning/Compatibility) do
CORE_HARDENING_PLAN de forma **aditiva** sobre as unidades 8.1–8.5:
máquina de transições de lifecycle, registo de extensões e
versioning/compatibilidade de `contract_version` com rejeição antes da
execução. Sem alterar `src/wsai2/extension/base.py` (contrato frozen
consumido via `TYPE_CHECKING` por `core/context` e `resource/governor`).

## Auditoria (estado real)

- `wsai2/extension` tem apenas `base.py` (contrato declarativo:
  `ExtensionKind`, `ExtensionLifecycleState` com 10 estados, `ResourceLimit`,
  `ExtensionContract` com `version`/`contract_version` strings) e
  `__init__.py`. Sem registo, sem transições, sem versioning, sem validação.
- Sem `ExtensionRegistry` nem "RuntimeStatus" — corrigir a referência a
  `RuntimeStatus` no `PROJECT_STATE.md` (suposição anterior não existente).
- Padrões a reutilizar: registries de `capability`/`model`/`provider`;
  `ValidationError` da taxonomia 8.2 para erros de validação.

## Ficheiros novos

1. `src/wsai2/extension/versioning.py`
   - `ContractVersion(major, minor)` frozen, `parse("N.N")` → `ValidationError`
     (`wsai.extension.contract_version`) em formato inválido.
   - `is_compatible_with(outra)`: `self.major == outra.major` (decisão
     registada: compatível dentro do mesmo major; minor é informativo).
   - `SUPPORTED_CONTRACT_VERSION = "1.0"`.

2. `src/wsai2/extension/lifecycle.py`
   - Diagrama de transições (dataclass p/ mapear) coerente com o
     hardening 02: DISCOVERED→(VALIDATED,FAILED); VALIDATED→
     (REGISTERED,FAILED); REGISTERED→(INITIALIZING,FAILED);
     INITIALIZING→(READY,FAILED); READY→(RUNNING,STOPPING,FAILED);
     RUNNING→(DEGRADED,FAILED,STOPPING); DEGRADED→(READY,FAILED,STOPPING);
     FAILED→(STOPPING); STOPPING→(STOPPED,FAILED); STOPPED terminal.
   - `valid_transitions(state)`, `can_transition(source, target)`,
     `transition(contract, target)` → `ExtensionContract` novo via
     `dataclasses.replace`; transição inválida → `ValidationError`
     (`wsai.extension.lifecycle`). Sem side effects (falha isolada).

3. `src/wsai2/extension/registry.py`
   - `ExtensionRegistry(supported_contract_version="1.0")`, padrão das
     Fases 4–6 (`get`, `has`, `all`, `__len__`, `unregister`).
   - `register(contract)`: id único (`wsai.extension.duplicate`), exige
     `lifecycle is VALIDATED` (`wsai.extension.lifecycle`), valida
     `contract_version` compatível com o núcleo
     (`wsai.extension.contract_incompatible`) e move para `REGISTERED`.
   - `state(id)` / `transition_state(id, target)` (desconhecido →
     `wsai.extension.unknown`).

4. `src/wsai2/extension/__init__.py` — exports novos (ContractVersion,
   SUPPORTED_CONTRACT_VERSION, ExtensionRegistry, valid_transitions,
   can_transition, transition).

## Testes (≈30 novos; baseline 314 → ≈344)

- `tests/test_extension_versioning.py` (~8): parse ok/inválido, formato,
  `str`, compatibilidade por major (minor irrelevante), constante 1.0.
- `tests/test_extension_lifecycle.py` (~10): diagrama por estado, transição
  válida (nova instância, originais intactos), inválida → ValidationError,
  cadeia completa DISCOVERED→…→RUNNING e FAILED→STOPPING→STOPPED, terminal.
- `tests/test_extension_registry.py` (~12): registo VALIDATED→REGISTERED,
  duplicados, estado errado no registo, contract_version inválida/incompatível,
  supported inválido, get/has/all/len, state/transition_state, unregister.

Validação: `py -3.12 -m pytest -q` (exit 0).

## Documentação

- `docs/extension/BASE-30-extension-lifecycle-compatibility.md` (relatório
  da base: decisões = compatibilidade por major, book de estados no
  contrato, falha de addon nunca derruba o núcleo).
- `PROJECT_STATE.md`: 8.6 concluída; remover menção a `RuntimeStatus`
  (estado = lifecycle do contrato no registo); baseline 344; próxima 8.7
  (testes de contrato arquitectural); barra Runtime Engine ~86%.
- `IMPLEMENTATION_LOG.md` (entrada 8.6).
- `CORE_HARDENING_PLAN.md`: estado IMPLEMENTADO nos blocos 02 e 08.
- `ARCHITECTURE.md` §3.8 (adicionar 8.6).

## Git

Commit único descritivo em `main` (ex.: "feat: lifecycle e compatibilidade
da Fase 8 (8.6)") + push para `origin/main` + verificação do estado.

## Riscos

- BAIXO de regressão: módulos novos, `base.py` intacto, base 314 intacta.
- MÉDIO de decisão: semântica de `contract_version` (registada: major).
- 8.7 (testes de contrato arquitectural) segue-se no mesmo caminho, sem
  bloqueio material.