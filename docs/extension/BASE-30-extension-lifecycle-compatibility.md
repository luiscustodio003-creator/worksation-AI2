# WORKSTATION AI 2 — RELATÓRIO DA BASE: EXTENSION LIFECYCLE + COMPATIBILITY

## O que foi feito

Foi implementada a unidade **Fase 8.6** dos dois hardening que faltavam
à camada de extensões: o **ciclo de vida** (hardening 02) e a
**compatibilidade de contratos** (hardening 08). Três novos módulos no
subsistema `wsai2.extension`:

- `versioning.py` — leitura semântica da `contract_version` (formato
  `major.minor`) e a regra de compatibilidade adoptada;
- `lifecycle.py` — a máquina de transições do diagrama do hardening 02;
- `registry.py` — o `ExtensionRegistry`, catálogo com barreiras de
  unicidade, compatibilidade e estado **antes** do registo.

A unidade é **100% aditiva**: o contrato declarativo `base.py` (8.1) não
foi alterado e nenhum módulo das Fases 1–7 nem das unidades 8.2–8.5 foi
tocado.

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8), pontos do
  CORE_HARDENING_PLAN: hardening 02 (security hardening — ciclo de vida
  de extensões e isolamento de falhas) e hardening 08 (compatibilidade e
  versioning de contratos).
- Estende a **Fase 8.1** sem a quebrar: o contrato ganha uma semântica
  para a `contract_version` que já declarava e uma máquina de estado
  coerente com a enumeração `ExtensionLifecycleState` que já expunha.
- Direcção das dependências mantida para dentro: `lifecycle`, `registry`
  e `versioning` dependem de `wsai2.core.errors` e do próprio `base.py`;
  são folhas do subsistema de extensões.
- **Correcção de registo persistente:** o relatório BASE-29 e o
  `PROJECT_STATE` referiam um "RuntimeStatus guardado no registo" como
  existente nas unidades anteriores. A auditoria pré-8.6 mostrou que essa
  entidade **não existe** e que o estado de uma extensão é o próprio
  campo `lifecycle` do `ExtensionContract`. O termo foi removido do
  estado do projecto; não foi criada nenhuma entidade nova — o
  `ExtensionRegistry` mantém o estado no contrato, sem duplicação.

## Para que serve

- **Garantir que nenhuma extensão incompatível é registada nem
  executada** (hardening 08): a `contract_version` é interpretada no
  registo (`major.minor`) e majors diferentes do contrato suportado pelo
  núcleo são rejeitados com `wsai.extension.contract_incompatible`,
  **antes** de qualquer estado operacional.
- **Governar o ciclo de vida sem efeitos laterais no núcleo** (hardening
  02): o `lifecycle` é uma máquina pura — valida a transição e devolve um
  novo contrato; nunca lança, descarrega ou reserva recursos. Uma
  transição inválida é um `ValidationError` (`wsai.extension.lifecycle`)
  observável e sem mutação de estado global: é a materialização do
  isolamento de falhas ("um addon avariado não derruba o Core").
- **Servir de catálogo único** nas unidades seguintes (8.7 e Runtime
  Engine de extensões): o `ExtensionRegistry` segue exactamente o padrão
  dos registos das Fases 4–6 (`get`/`has`/`all`/`__len__`/`unregister`),
  de modo a não introduzir mais do que um padrão de registo no sistema.

## Ficheiros criados/alterados

- `src/wsai2/extension/versioning.py` — `ContractVersion` (frozen),
  `SUPPORTED_CONTRACT_VERSION = "1.0"`, `parse` e `is_compatible_with`
- `src/wsai2/extension/lifecycle.py` — `_DIAGRAMA`,
  `valid_transitions`, `can_transition`, `transition`
- `src/wsai2/extension/registry.py` — `ExtensionRegistry`
  (`register`, `unregister`, `get`, `has`, `all`, `state`,
  `transition_state`, `supported_contract_version`)
- `src/wsai2/extension/__init__.py` — novos exports públicos (o
  `base.py` não foi alterado)
- `tests/test_extension_versioning.py` — 17 testes
- `tests/test_extension_lifecycle.py` — 10 testes
- `tests/test_extension_registry.py` — 13 testes
- `docs/extension/BASE-30-extension-lifecycle-compatibility.md` — este relatório

## Dependências

- `versioning.py`: `wsai2.core.errors` (`ValidationError`) e stdlib
  (regex, dataclasses).
- `lifecycle.py`: `wsai2.core.errors` e `.base` (`ExtensionContract`,
  `ExtensionLifecycleState`).
- `registry.py`: `wsai2.core.errors`, `.base`, `.lifecycle` e
  `.versioning` — todos dentro do próprio subsistema ou do core.
- **Não duplica**: não existe outro registo de extensões, outra máquina
  de lifecycle ou outra leitura de versões de contrato no repositório.

## Decisões arquitecturais registadas

1. **Compatibilidade = mesmo `major`;** formato `major.minor` (sem
   patch). `minor` é informativo; dentro do mesmo major presume-se
   retrocompatibilidade. A `version` do addon continua opaca (só se exige
   não vazia, validado na 8.1) — não é interpretada.
2. **Rejeição antes do registo/execução:** o `register` valida
   `ContractVersion.parse` e `is_compatible_with` como barreiras de
   entrada (hardening 08), devolvendo erros com código próprio
   (`wsai.extension.contract_version` /
   `wsai.extension.contract_incompatible`) e **sem registar** a extensão.
3. **Estado no contrato, não entidade nova:** o estado de lifecycle é o
   campo `lifecycle` do `ExtensionContract`; o registo guarda o contrato
   (avançado via `transition`), não um "RuntimeStatus" paralelo.
4. **`register` exige `VALIDATED`** e move para `REGISTERED`: o fluxo
   DISCOVERED→VALIDATED é feito por quem invoca (com `transition`), o
   registo apenas o confirma como pré-condição — coerente com o diagrama
   do hardening 02.
5. **Lifecycle puro e sem efeitos laterais:** `transition` valida e
   devolve `replace(...)` de um contrato `frozen`; nunca executa acções
   de sistema. Transições inválidas são sempre `ValidationError` de um
   único código (`wsai.extension.lifecycle`), com origem e destino nos
   `details`.
6. **Registo desacoplado do arranque:** o registo não executa addons nem
   gere recursos — a 8.4/8.5 e as unidades de arranque de extensões são
   posteriores; evitar antecipar responsabilidades (constituição, art. 3).

## Testes

Executado com:

```text
py -3.12 -m pytest
```

Resultado: **354 testes aprovados** (40 novos desta unidade + 314 bases
anteriores). Regressão intacta — alteração 100% aditiva.

Cobertura dos 40 novos testes:

- **versioning (17):** parse de `major.minor` (incluindo múltiplos
  dígitos e espaços); rejeição de formatos inválidos (parametrizado, 10
  casos) com `wsai.extension.contract_version`; imutabilidade;
  compatibilidade por major (iguais/inferiores) e incompatibilidade por
  major distinto; constante suportada.
- **lifecycle (10):** caminho feliz DISCOVERED→…→STOPPED; devolve novo
  contrato sem mutar o original; falha alcançável de todos os estados
  activos; saída de FAILED apenas via STOPPING; STOPPED terminal; saídas
  de READY; transição inválida com código e details (origem/destino);
  diagrama cobre todos os estados do enum; transições sempre do mesmo
  enum.
- **registry (13):** register marca REGISTERED; duplicado
  (`wsai.extension.duplicate`); versão suportada por defeito; contrato
  2.x rejeitado antes de registar; versão mal formada rejeitada; minor
  dentro do mesmo major aceite; exigência de VALIDATED; consultas
  get/has/all/len; unregister; `state`/`transition_state` com extensão
  desconhecida (`wsai.extension.unknown`); transição inválida não corrompe
  o catálogo.

## Estado da fase

Fase 8 — Runtime Engine: **8.6 concluída**. Concluídas: 8.1 (contrato),
8.2 (contexto + erros), 8.3 (governação de recursos), 8.4 (políticas de
execução anticorrupção), 8.5 (Runtime Manager + scheduler) e 8.6
(lifecycle + compatibilidade). Falta **8.7 — testes de contrato
arquitectural** (hardening 10) e as unidades de execução efectiva de
extensões / concorrência (ainda não anunciadas, fora da 8.6).

## Riscos residuais

- A compatibilidade por major é conservadora: um major futuro (ex.: 2.x)
  exige evolução do núcleo, por decisão deliberada. Uma política
  "semVer completa" (minor) seria mais permissiva e é adiada.
- O registo valida ordem e versão, mas **não valida o rótulo
  `ExtensionKind`** (lista aberta) — não é exigido por nenhuma unidade
  actual.
- A máquina de lifecycle é pura; a execução real das transições
  operacionais (realmente lançar/parar um addon) pertence a unidades
  posteriores, não anunciadas nesta base.

## Próximo passo

**Fase 8.7 — Testes de contrato arquitectural** (hardening 11): testes
que verificam as regras da CONSTITUTION/AGENTS no repositório (fronteiras
de dependências, ausência de ciclos de import, isolamento de código
Windows/Linux, documentação por módulo). Sem decisão arquitectural nova —
execução directa da próxima unidade.