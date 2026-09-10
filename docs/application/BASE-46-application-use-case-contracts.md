# WORKSTATION AI 2 — BASE-46: APPLICATION — CONTRATOS DE USE-CASE (APP-02)

## Responsabilidade

Camada Application do WSAI 2 (subsistema `wsai2.application`, fase Pós-Kernel /
Ramo A): definir a **fronteira estável dos use-cases** — mensagens puras de
pedido/resposta por área — reutilizando os tipos públicos de domínio
existentes (REUSE, constituição artigo 6). A Application **não contém lógica
central de negócio**: tipa apenas payloads produzidos pelo núcleo e pelos
subsistemas de domínio (artigo 7).

## Âmbito (APP-02)

- Contratos `@dataclass(frozen=True)` para 8 áreas de use-case:
  - System/Platform (`SystemInfoRequest`/`SystemInfoResponse`, APP-03);
  - Hardware (`HardwareProfileRequest`/`HardwareProfileResponse`, APP-04);
  - Runtime (`RuntimeProfileRequest`/`RuntimeProfileResponse`, APP-05);
  - Capabilities (`CapabilitiesRequest`/`CapabilitiesResponse`, APP-06);
  - Models (`ModelsRequest`/`ModelsResponse`, APP-07);
  - Tasks (`TaskAnalysisRequest`/`TaskAnalysisResponse`, APP-08);
  - Knowledge (`KnowledgeContextRequest`/`KnowledgeContextResponse`, APP-09);
  - Execution/Status/Cancellation (`ExecutionRequest`/`ExecutionResponse`,
    `ExecutionStatusRequest`/`ExecutionStatusResponse`,
    `CancellationRequest`/`CancellationResponse`, APP-10).
- Regras mínimas de validação por contrato (consultas não vazias, limites e
  timeouts positivos, identificadores não vazios) — nada mais.
- Autorização de `application` na fonte única: arestas `FRONTEIRAS` em
  `superficies`, `FIREWALL["application"]`, `SUPERFICIES_PUBLICAS["application"]`
  (20 símbolos), `MODULO_CONTRATO`/`CONTRATO_CONSTANTES` e
  `CONTRACT_VERSIONES["application"] = "1.0"`.
- Exposição aditiva de `PlatformInfo` em `wsai2.platform` (necessária para os
  contratos consumirem a plataforma **ao nível do pacote**, regra KERNEL de
  fronteira).

**Fora do âmbito (unidades seguintes):** adaptadores de resolver/executor dos
use-cases (APP-03+), integração da API com estes contratos (API-02+) e a UI.

## Dependências

- `application → capability, core, hardware, knowledge, model, platform,
  runtime, runtime_engine, task` — todas ao nível do pacote
  (`wsai2.<subsistema>`), nunca módulos internos.
- Nenhuma biblioteca externa; zero I/O, transporte ou persistência.
- Direcção: a API consome estes contratos (constituição artigo 7); a
  Application **não** conhece a API.

## Interfaces

```python
APPLICATION_CONTRACT_VERSION == "1.0"          # fora de __all__

# System/Platform (APP-03)
SystemInfoRequest()                            # sem parâmetros
SystemInfoResponse(platform: PlatformInfo, uptime: SystemUptime | None = None)

# Hardware (APP-04)
HardwareProfileRequest()
HardwareProfileResponse(profile: HardwareProfile)

# Runtime (APP-05)
RuntimeProfileRequest()
RuntimeProfileResponse(profile: RuntimeProfile)

# Capabilities (APP-06)
CapabilitiesRequest(domain: CapabilityDomain | None = None)
CapabilitiesResponse(report: CompatibilityReport)

# Models (APP-07)
ModelsRequest(category: ModelCategory | None = None)
ModelsResponse(verdicts: tuple[ModelVerdict, ...] = ())

# Tasks (APP-08)
TaskAnalysisRequest(task: Task)
TaskAnalysisResponse(task_id, classification, requirements,
                     selection=None, plan=None)

# Knowledge (APP-09)
KnowledgeContextRequest(query: str, limit: int = 8, kind: KnowledgeKind | None = None)
KnowledgeContextResponse(query, matches: tuple[KnowledgeRecord, ...] = (), context=None)

# Execution/Status/Cancellation (APP-10)
ExecutionRequest(task: Task, priority=ExecutionPriority.NORMAL, timeout_seconds=None)
ExecutionResponse(task_id, plan=None, report=None)
ExecutionStatusRequest(execution_id: str)
ExecutionStatusResponse(execution_id, status=None, snapshot=None, report=None)
CancellationRequest(execution_id: str)
CancellationResponse(execution_id: str, cancelled: bool)
```

## Decisões

1. **Contract-first puro** — os contratos são dataclasses imutáveis sem
   comportamento; a validação limita-se a invariantes de forma (não há
   avaliação de exequibilidade, selecção de modelos ou construção de contexto
   na Application).
2. **REUSE de superfícies públicas** — cada resposta tipa directamente os
   tipos de domínio (`PlatformInfo`, `HardwareProfile`, `RuntimeProfile`,
   `CompatibilityReport`, `ModelVerdict`, `Task*`, `Knowledge*`,
   `Execution*`) ao nível do pacote; não há cópias de estrutura nem módulos
   internos importados.
3. **Cobertura 1:1 com o Ramo A** — um par pedido/resposta por use-case do
   roadmap; os próximos passos (APP-03..APP-10) constroem os adaptadores que
   satisfazem estes contratos, mantendo a fronteira estável.
4. **Exposição aditiva de `PlatformInfo`** — o tipo já existia em
   `wsai2.platform.base`; sai agora na superfície do pacote para que o
   consumidor respeite a regra de consumo ao nível do pacote.

## Validação

```text
py -m pytest
tests=~520  failures=0  errors=0  skipped=0
(513 bases + 16 novos: 14 contratos/validações + 1 superfície + 1 fronteira)
```

- Fonte única actualizada (`FRONTEIRAS`, `FIREWALL`, `SUPERFICIES_PUBLICAS`,
  `MODULO_CONTRATO`, `CONTRATO_CONSTANTES`, `CONTRACT_VERSIONES`);
- testes de fronteira e arquitectura verificam docstrings, base documental,
  acyclicidade, firewall exacto e ausência de placeholders para `application`.