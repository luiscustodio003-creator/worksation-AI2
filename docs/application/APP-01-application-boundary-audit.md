# APP-01 — APPLICATION BOUNDARY AUDIT (auditoria de base)

**Data:** 2026-09-10
**Branch:** main (Ramo A — Application / Use-Case Boundary)
**Modo:** `/wsai-run APP-01` (auditoria read-only)
**Estado arquitectura:** FROZEN (Kernel consolidado; API-01 concluída)
**Código alterado:** nenhum (auditoria read-only)
**Verificação:** 513/513 testes verdes (`py -3.12 -m pytest`, `exit 0`)

## 1. Âmbito

Unidade APP-01 do Ramo A — Application / Use-Case Boundary, conforme
`docs/project/PROJECT_STATE.md` e `docs/project/ROADMAP.md`. O objectivo é
**inventariar e classificar responsabilidades existentes, consumidores,
contratos, serviços e adaptadores** antes de qualquer criação de código na
camada Application. A fonte é o código real (`src/wsai2`), os testes e a
fonte única de arquitectura (`tests/architecture_contracts.py`), não
suposições nem documentação futura.

## 2. Inventário real

85 ficheiros Python / 16 subsistemas (fonte: scan real `src/wsai2`):

| Subsistema | Responsabilidade | Ficheiros |
|---|---|---|
| `core` | Núcleo folha: erros transversais + contexto/cancelamento | 4 (inclui `public.py`) |
| `execution` | Políticas de execução (timeout, cancelamento, recuperação) | 3 |
| `resource` | Governação de recursos (shell de re-export) | 1 |
| `runtime_engine` | Gestor, scheduler, filas, monitorização (shell de re-export) | 1 |
| `security` | Política + isolamento de projectos | 4 |
| `infrastructure` | Implementação pesada do kernel (por trás dos contratos) | 8 |
| `platform` | Isolamento Windows/Linux (adaptadores de SO) | 5 |
| `hardware` | Capacidade estrutural (CPU/GPU/memória/storage) | 8 |
| `runtime` | Estado efectivo (CPU/memória/processos/availability) | 7 |
| `capability` | Capacidades: registo, avaliação, compatibilidade | 5 |
| `model` | Modelos: registo, classificação, compatibilidade, recomendação | 6 |
| `provider` | Fornecedores: detecção, probes, health, transportes, adaptadores | 8 |
| `task` | Tarefas: contrato, requisitos, classificação, selecção, plano | 6 |
| `knowledge` | Knowledge Engine 9.1–9.7 (contrato→registo→metadados→índice→SQLite→contexto→ingestão) | 8 |
| `extension` | Contrato de addon: contrato, lifecycle, versioning, registo | 5 |
| `api` | Camada Application: fundação contract-first (API-01) | 4 |
| — | `wsai2/__init__.py`, `wsai2/version.py` | 2 |

## 3. Classificação por camada arquitectural

- **Kernel / Core (FROZEN):** `core`, `execution`, `resource`,
  `runtime_engine`, `security`.
- **Infraestrutura:** `infrastructure` (implementação pesada por trás dos
  contratos públicos) e `platform` (adaptadores de SO, isolados pela
  Constituição).
- **Subsistemas de domínio:** `hardware`, `runtime`, `capability`, `model`,
  `provider`, `task`, `knowledge`.
- **Contrato addon:** `extension` (`EXTENSION_CONTRACT_VERSION = "1.0"`).
- **Application:** `api` (fundação API-01). **Camada Application de
  use-cases: NÃO EXISTE em `src/wsai2`** — é o trabalho do Ramo A.
- **Futuros previstos:** `ui` (`SUBSISTEMAS_FUTUROS = ("ui",)`); addons
  Projects/embeddings (gates próprios).

## 4. Contratos públicos existentes (superfícies versionadas)

| Contrato | Local | Versão | Símbolos |
|---|---|---|---|
| `core.public` | `wsai2.core.public` | `1.0` | 11 erros + contexto/cancelamento/prioridade + versão |
| `api` | `wsai2.api` | `1.0` | `ApiGateway`, `ApiRequest`, `ApiResponse`, `StdLibHttpGateway`, `health` |
| `execution` | `wsai2.execution` | `1.0` | 7 |
| `resource` | `wsai2.resource` | `1.0` | 7 |
| `security` | `wsai2.security` | `1.0` | 6 |
| `runtime_engine` | `wsai2.runtime_engine` | `1.0` | 16 |
| `extension` (addon) | `wsai2.extension` | `1.0` | 10 |

Subsistemas de domínio sem constante de versão de contrato, mas com
`__all__` público no nível do pacote: `hardware` (13), `runtime` (10),
`capability` (14), `model` (21), `provider` (24), `task` (14),
`knowledge` (15). A semântica dos contratos está em
`tests/architecture_contracts.py` (`FRONTEIRAS`, `FIREWALL`,
`SUPERFICIES_PUBLICAS`, `CONTRACT_VERSIONES`, `MODULO_CONTRATO`).

## 5. Serviços existentes (mecânicas orquestradoras reutilizáveis)

A Application de use-cases não precisa de recriar domínio — os serviços
seguintes são as superfícies de orquestração já disponíveis:

| Área | Serviços |
|---|---|
| `hardware` | `discover_hardware()`, `discover_gpus()`, `discover_storage()` |
| `runtime` | `discover_runtime()`, `analyze_runtime_availability()` |
| `capability` | `create_default_registry()`, `evaluate_capability()`, `evaluate_capabilities()`, `available_capabilities()`, `build_compatibility()` |
| `model` | `create_default_registry()`, `classify_model(s)`, `category_for()`, `evaluate_model(s)`, `compatible_models()`, `recommend_model()`, `adequacy_score()` |
| `provider` | `detect_provider(s)`, `available_providers()`, `build_adapter()`, `adapter_factory_names()`, `check_provider_health(s)`, `healthy_providers()`, `health_probe()` |
| `task` | `classify_task(s)`, `category_for_task()`, `requirements_for(_many)`, `capabilities_for_task()`, `select_capabilities()`, `build_execution_plan()` |
| `knowledge` | `tokenize()`, `detect_language()`, `derive_tags()` + `KnowledgeRegistry`, `KnowledgeIndex`, `KnowledgeStore`, `ContextBuilder`, `FileIngestor` |
| `execution` | `run_with_timeout()`, `run_with_recovery()`, `execute_with_policies()` |
| `runtime_engine` | `Scheduler.run()`, `RuntimeManager.execute_plan()`, `MultilayerExecutionQueue`, `ExecutionMonitor.snapshot()` |
| `resource` | `ResourceGovernor.{evaluate,allocate,release,outstanding,committed_for}` |
| `security` | `PolicyEngine`, `require_project()`, `assert_same_project()` |
| `extension` | `ExtensionRegistry`, `can_transition()`, `transition()`, `ContractVersion` |

## 6. Adaptadores existentes

- **Plataforma (SO):** `wsai2.platform.windows`, `wsai2.platform.linux` —
  acesso reservado, consumidos apenas pelas fábricas de hardware/runtime.
- **Provider:** `OllamaAdapter`, `OpenAiCompatibleAdapter` (por trás do
  protocolo `RuntimeAdapter`, com `Transport`/`TransportResult`
  injectáveis), `http_json_transport()`.
- **API (transporte):** `ApiGateway` (porte injectável) +
  `StdLibHttpGateway` sobre `http.server` (JSON, 404/405 antes de handlers).
- **Knowledge (persistência/ingestão):** `KnowledgeStore` (SQLite),
  `FileIngestor` (tipos de ficheiro de texto do projecto).

Todos os adaptadores são injectáveis/reversíveis; nenhum entra no domínio.

## 7. Consumidores actuais

- **Consumidores internos do kernel** (scan AST real; `FRONTEIRAS`):
  `execution→{core,resource}`; `resource→{infrastructure}`;
  `runtime_engine→{infrastructure}`; `security→{core}`;
  `extension→{core,security}`;
  `infrastructure→{core,execution,extension,hardware,runtime,security,task}`;
  `knowledge→{core}`; `model→{capability,hardware,runtime}`;
  `task→{capability,hardware,model,provider,runtime}`;
  `capability→{hardware,runtime}`; `core→{extension}`.
- **Consumidores externos:** nenhum. O único subsistema da camada
  Application presente (`api`) consome apenas `wsai2.core.public` (regra
  KERNEL-08). Nenhuma aplicação/CLI/UI consome os serviços de domínio.
- Grafo de imports **acíclico** (verificado na suíte).

Conclusão operacional: a Application de use-cases será o **primeiro
consumidor orquestrado** das superfícies de domínio, e não um recriador
delas.

## 8. Fronteira e firewall aplicáveis à Application

- Regra actual: `FIREWALL["api"] = {"core"}`; aresta única
  `("api", "core")`; recursos de domínio entram por unidades com arestas
  específicas justificadas e cobertas por teste AST (decisão API-01).
- Direcção imposta pela Constituição (art. 2, 6, 7): o domínio não conhece
  a Application; a Application **expõe as superfícies públicas do núcleo e
  dos subsistemas**, não contém lógica central de decisão.
- `COMMAND_EXECUTION_CONTRACT.md`: `Application → Core Public API`;
  a Application não pode criar implementação pesada paralela aos domínios.
- A decisão exacta `application → api` ou `api → application` (e as arestas
  concretas por recurso) é **decisão material de APP-02** — não é resolvida
  nesta auditoria.

## 9. Observações / problemas

- **P3 — ESTRUTURAL:** não existe pacote `wsai2.application`/use-cases —
  esperado, é o objectivo do Ramo A; a auditoria fornece a base para o
  não duplicar.
- **P3 — FRONTEIRA:** a divisão exacta entre use-cases da Application e
  handlers da API (fronteira `application↔api`) está em aberto — a resolver
  em APP-02 (ARQ) antes de criar código; impacto: semântica de
  `FIREWALL["api"]` e novas arestas.
- **P3 — CONTRATOS:** os subsistemas de domínio não possuem constante de
  versão de contrato (apenas `__all__`); a Application deve consumi-los
  pelas superfícies públicas já existentes, mantendo a convenção.
- **P3 — REUTILIZAÇÃO (positiva):** os registos/evaluators/discoverers de
  todos os domínios estão prontos para orquestração por use-cases — não
  existem lacunas estruturais de domínio que exijam `CREATE` para APP-03..09.

## 10. Riscos

- **R1 — MÉDIO:** criar use-cases que dupliquem serviços/repositórios de
  domínio → mitigado por `REUSE → ADAPT → WRAP/ADAPTER → EXTEND → CREATE`
  e por esta auditoria.
- **R2 — MÉDIO:** decidir a fronteira `application↔api` sem ARQ → pode
  virar a API num duplicador de use-cases. Mitigação: decisão em APP-02 com
  arestas cobertas por teste.
- **R3 — BAIXO:** arestas novas da Application para domínio exigirem
  actualização da fonte única (`FRONTEIRAS`/`FIREWALL`) — processo normal,
  coberto pela suíte de contrato arquitectural.
- **R4 — INFORMATIVO:** não reverter o fecho do Kernel; qualquer exposição
  de superfície passa pela fonte única versionada.

## 11. Recomendação

PRÓXIMA UNIDADE — `/wsai-plan APP-02 — Use-Case Contracts`: definir os
contratos de use-case (pedido/resposta puros) por área
(system/platform, hardware, runtime, capabilities, models, tasks,
knowledge, execution/status/cancelamento), **reutilizando** as superfícies
públicas listadas acima e **decidindo em ARQ** a fronteira
`application↔api` e as arestas de consumo por recurso. Risco MÉDIO, sem
bloqueadores P0/P1/P2.

## 12. Conclusão

Unidade documental APP-01 **concluída** sem alteração de código. Suíte
completa: **513/513 verdes**. Base estabelecida para a definição de
contratos de use-case (APP-02) e para o fecho do Ramo A sem duplicação de
domínio.