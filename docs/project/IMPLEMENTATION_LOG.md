# WORKSTATION AI 2 — IMPLEMENTATION LOG

## 2026-09-08 — Task Intelligence (plano de execução) — Fase 7

### Objectivo

Integrar os requisitos, a viabilidade, a recomendação de modelo e um
fornecedor saudável num plano de execução determinístico, encerrando a
Fase 7.

### Criado

- `src/wsai2/task/plan.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_plan.py`
- `docs/task/BASE-24-task-intelligence-execution-plan.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
`build_execution_plan` fecha o ciclo (requisitos → capacidades →
modelo → fornecedor saudável → passos). A selecção de modelo e de
fornecedor permanece separada (constituição, artigo 13); o health check
dos fornecedores é injectado (`ProviderHealth`), sem I/O no plano.

### Resultado

`ExecutionPlan` (feasible, model_id, provider_id, reasons, steps) com
`is_executable`; escolha do fornecedor determinística (saudável + com
capacidades do modelo) e justificações de inviabilidade.

### Validação

```text
py -3.12 -m pytest -v   →   209 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 39 task)
```

### Próximo passo

Iniciar a Fase 8 — Runtime Engine (subsistema 3.8).

---

## 2026-09-08 — Task Intelligence (selecção de capacidades) — Fase 7

### Objectivo

Verificar, contra o Capability Engine, quais das capacidades exigidas
por uma tarefa estão disponíveis, determinando a viabilidade da
execução.

### Criado

- `src/wsai2/task/capability_selection.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_capability_selection.py`
- `docs/task/BASE-23-task-intelligence-capability-selection.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
A selecção delega a avaliação ao Capability Engine (Fase 4); o Task
Intelligence separa capacidades satisfeitas e em falta e decide a
viabilidade, sem duplicar lógica.

### Resultado

`select_capabilities` devolve `TaskCapabilitySelection` (required /
available / missing / is_viable), preservando a ordem de declaração.

### Validação

```text
py -3.12 -m pytest -v   →   201 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 31 task)
```

### Próximo passo

Concluir a Fase 7 (plano de execução).

---

## 2026-09-08 — Task Intelligence (requisitos de tarefa) — Fase 7

### Objectivo

Materializar as exigências de uma tarefa (categoria, capacidades,
tokens) num contrato consumível pelo Model Intelligence.

### Criado

- `src/wsai2/task/requirements.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_requirements.py`
- `docs/task/BASE-22-task-intelligence-requirements.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
`TaskRequirements` agrega a categoria (da classificação) e as
capacidades exigidas pela tarefa — únicas, por ordem, sem invenção
(limite BASE-19).

### Resultado

`requirements_for` / `requirements_for_many` devolvem o contrato de
requisitos das tarefas; `capabilities_for_task` normaliza a lista.

### Validação

```text
py -3.12 -m pytest -v   →   194 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 24 task)
```

### Próximo passo

Continuar a Fase 7 (selecção de capacidades contra o Capability Engine).

---

## 2026-09-08 — Task Intelligence (classificação de tarefas) — Fase 7

### Objectivo

Classificar cada tarefa quanto à categoria de modelo mais adequada,
ligando o Task Intelligence ao Model Intelligence de forma
determinística.

### Criado

- `src/wsai2/task/classification.py`
- Actualizado `src/wsai2/task/__init__.py`
- `tests/test_task_classification.py`
- `docs/task/BASE-21-task-intelligence-classification.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
`TaskClassification` mapeia o tipo funcional (TaskKind) para a
categoria de modelo (ModelCategory); a selecção de modelo e de
fornecedor permanece separada (constituição, artigo 13).

### Resultado

`classify_task` / `classify_tasks` devolvem a categoria adequada por
tarefa, com mapa determinístico documentado e ordem preservada.

### Validação

```text
py -3.12 -m pytest -v   →   186 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 16 task)
```

### Próximo passo

Continuar a Fase 7 (requisitos de tarefa).

---

## 2026-09-08 — Task Intelligence (contrato de tarefa) — Fase 7

### Objectivo

Iniciar a Fase 7 — Task Intelligence com o contrato de tarefa e a sua
representação, como definido na auditoria BASE-19.

### Criado

- `src/wsai2/task/base.py`
- `src/wsai2/task/__init__.py`
- `tests/test_task.py`
- `docs/task/BASE-20-task-intelligence-contract.md`

### Arquitectura abrangida

Fase 7 — Task Intelligence. Subsistema 3.7 da arquitectura.
A tarefa declara o que fazer (tipo funcional, texto, capacidades) sem
depender de modelos ou fornecedores (constituição, artigo 13).

### Resultado

`TaskKind` (chat / completion / embedding) e `Task` imutável com
`required_capabilities` e `metadata` opaca; valida prompt e max_tokens.

### Validação

```text
py -3.12 -m pytest -v   →   179 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider + 9 task)
```

### Próximo passo

Continuar a Fase 7 (classificação de tarefas).

---

## 2026-09-07 — Provider Layer (health checks) — Fase 6

### Objectivo

Concluir o Provider Layer com a saúde fina dos fornecedores
(saudável / degradado / indisponível), combinando detecção e
adaptadores, encerrando a Fase 6.

### Criado

- `src/wsai2/provider/health.py`
- Actualizado `src/wsai2/provider/__init__.py`
- `tests/test_provider_health.py`
- `docs/provider/BASE-18-provider-layer-health.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
Os health checks consomem a detecção e os adaptadores; a decisão é
pura e o I/O (probe + transporte) injectado. Fornecedores sem
adaptador são reportados como DEGRADED (não propagam erros).

### Resultado

`check_provider_health` / `check_providers_health` devolvem `ProviderHealth`
com contagem de modelos, latência e erro; `healthy_providers` filtra os
operacionais. Integração real validada contra servidor local.

### Validação

```text
py -3.12 -m pytest -v   →   170 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 46 provider)
```

### Próximo passo

Iniciar a Fase 7 — Task Intelligence (subsistema 3.7).

---

## 2026-09-07 — Provider Layer (adaptadores de runtime) — Fase 6

### Objectivo

Definir a interface estável de comunicação com os motores concretos
(listar modelos, gerar texto) por tipo de fornecedor, mantendo o I/O de
rede injectável e isolado do domínio.

### Criado

- `src/wsai2/provider/adapters.py`
- `src/wsai2/provider/transports.py`
- Actualizado `src/wsai2/provider/__init__.py`
- `tests/test_provider_adapters.py`
- `docs/provider/BASE-17-provider-layer-adapters.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
`RuntimeAdapter` (Protocol) com `OllamaAdapter` (protocolo nativo) e
`OpenAiCompatibleAdapter` (llama.cpp e APIs compatíveis); `build_adapter`
constrói por id de fornecedor; `http_json_transport` separa o I/O.

### Resultado

Toda a lógica dos adaptadores é testável sem rede (transport
injectável); erros normalizados em `AdapterError`; fábrica de
adaptadores por id cobrindo todo o catálogo base.

### Validação

```text
py -3.12 -m pytest -v   →   160 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 36 provider)
```

### Próximo passo

Concluir a Fase 6 (health checks: saúde fina por fornecedor).

---

## 2026-09-07 — Provider Layer (detecção) — Fase 6

### Objectivo

Detectar no ambiente real quais fornecedores do registo estão presentes
e acessíveis, separando a lógica de domínio do I/O de rede.

### Criado

- `src/wsai2/provider/detection.py`
- `src/wsai2/provider/probes.py`
- Actualizado `src/wsai2/provider/__init__.py`
- `tests/test_provider_detection.py`
- `docs/provider/BASE-16-provider-layer-detection.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
A detecção mantém o domínio puro (`detection.py`) e isola o contacto de
rede em probes injectáveis (`probes.py`), respeitando o artigo 5 da
constituição (código de I/O separado da lógica de domínio).

### Resultado

`detect_provider` / `detect_providers` devolvem `ProviderDetection`
(estado, latência, erro, capacidades) usando um `ProviderProbe`
injectável; `available_providers` filtra os acessíveis. `health_probe`
é o probe HTTP concreto isolado. Toda a lógica é testável sem rede.

### Validação

```text
py -3.12 -m pytest -v   →   146 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 22 provider)
```

### Próximo passo

Continuar a Fase 6 (adaptadores de runtime: interface estável de
comunicação por tipo de fornecedor).

---

## 2026-09-07 — Provider Layer (contratos e registo) — Fase 6

### Objectivo

Iniciar a Fase 6 — Provider Layer com os contratos de fornecedor e o
registo central, base declarativa para a detecção, os adaptadores e os
health checks das unidades seguintes.

### Criado

- `src/wsai2/provider/base.py`
- `src/wsai2/provider/registry.py`
- `src/wsai2/provider/__init__.py`
- `tests/test_provider.py`
- `docs/provider/BASE-15-provider-layer-contracts.md`

### Arquitectura abrangida

Fase 6 — Provider Layer. Subsistema 3.6 da arquitectura.
Isola os fornecedores e motores concretos (runtimes locais e APIs
compatíveis) através de contratos estáveis.

### Resultado

`ProviderDefinition` com `ProviderType` (local_runtime / remote_api),
endpoint base predefinido e `capabilities_provided` (ligação ao
Capability Engine). `ProviderRegistry` com catálogo base (Ollama,
llama.cpp, API compatível com OpenAI). Domínio puro, sem dependências de
plataforma.

### Validação

```text
py -3.12 -m pytest -v   →   135 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model + 11 provider)
```

### Próximo passo

Continuar a Fase 6 (detecção de fornecedores presentes e acessíveis no
ambiente real).

---

## 2026-09-07 — Model Intelligence (recomendação) — Fase 5

### Objectivo

Concluir a Fase 5 — Model Intelligence com a recomendação do modelo
mais adequado (por categoria e score), com justificação e alternativas.

### Criado

- `src/wsai2/model/recommendation.py`
- Actualizado `src/wsai2/model/__init__.py` (exporta novos tipos e função)
- `tests/test_model_recommendation.py`
- `docs/model/BASE-14-model-intelligence-recommendation.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Fecho do item "recomendação" do roadmap da fase. Política determinística
documentada: candidatos com score > 0; ordenação por score, parâmetros,
RAM e id.

### Resultado

`recommend_model` devolve `ModelRecommendation` (modelo, categoria,
score, estado, razão e alternativas) ou `None` sem candidatos. Modelos
indisponíveis nunca são recomendados.

### Validação

```text
py -3.12 -m pytest -v   →   124 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 42 model)
```

### Próximo passo

Iniciar a Fase 6 — Provider Layer (subsistema 3.6): contratos de
fornecedor, detecção, adaptadores de runtime e health checks.

---

## 2026-09-07 — Model Intelligence (classificação) — Fase 5

### Objectivo

Implementar a classificação dos modelos: categoria funcional primária e
score de adequação determinístico derivado da compatibilidade, base
para a recomendação.

### Criado

- `src/wsai2/model/classification.py`
- Actualizado `src/wsai2/model/base.py` (ModelCategory; campo category em ModelDefinition)
- Actualizado `src/wsai2/model/registry.py` (catálogo com categorias)
- Actualizado `src/wsai2/model/__init__.py` (exporta novos tipos e funções)
- `tests/test_model_classification.py`
- `docs/model/BASE-13-model-intelligence-classification.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Rubrica de classificação determinística (disponível=1.0, condicionado=0.5,
indisponível=0.0) aplicada sobre os veredictos de compatibilidade.

### Resultado

`classify_model`/`classify_models` devolvem `ModelClassification`
(categoria + score + veredicto). Categoria declarada na definição ou
derivada do tipo (LLM → chat; embedding → embedding).

### Validação

```text
py -3.12 -m pytest -v   →   114 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 32 model)
```

### Próximo passo

Continuar a Fase 5 (recomendação de modelos — encerra a fase).

---

## 2026-09-07 — Model Intelligence (compatibilidade) — Fase 5

### Objectivo

Implementar a compatibilidade dos modelos contra o hardware
estrutural, o estado do runtime e as capacidades requeridas do
Capability Engine, preparando a classificação e a recomendação.

### Criado

- `src/wsai2/model/compatibility.py`
- Actualizado `src/wsai2/model/base.py` (ModelState, ModelCheck, ModelVerdict)
- Actualizado `src/wsai2/model/__init__.py` (exporta novos tipos e funções)
- `tests/test_model_compatibility.py`
- `docs/model/BASE-12-model-intelligence-compatibility.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Compatibilidade com tripla dimensão: capacidades requeridas (Capability
Engine), requisitos estruturais (*Hardware Capability*) e requisitos de
runtime (*Runtime State*) — Artigo 5 da Constituição.

### Resultado

`evaluate_model`, `evaluate_models` e `compatible_models` devolvem
`ModelVerdict` com `ModelState`, verificações por requisito e
capacidades em falta. Capacidade em falta ou requisito estrutural
falhado → UNAVAILABLE; capacidade condicionada ou runtime insuficiente
→ RESTRICTED; caso contrário → AVAILABLE.

### Validação

```text
py -3.12 -m pytest -v   →   105 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 23 model)
```

### Próximo passo

Continuar a Fase 5 (classificação dos modelos e score de adequação para
recomendação).

---

## 2026-09-07 — Model Intelligence (registo e metadados) — Fase 5

### Objectivo

Iniciar a Fase 5 — Model Intelligence com o registo de modelos,
metadados e requisitos, base declarativa para a compatibilidade e a
recomendação das unidades seguintes.

### Criado

- `src/wsai2/model/base.py`
- `src/wsai2/model/registry.py`
- `src/wsai2/model/__init__.py`
- `tests/test_model.py`
- `docs/model/BASE-11-model-intelligence-metadata.md`

### Arquitectura abrangida

Fase 5 — Model Intelligence. Subsistema 3.5 da arquitectura.
Mantém informação sobre modelos: metadados, requisitos e, nas unidades
seguintes, compatibilidade, desempenho e adequação às tarefas.

### Resultado

`ModelDefinition` com `ModelKind` (llm/embedding), `ModelMetadata`
(versão, parâmetros, janela de contexto, licença, arquitectura) e
`ModelRequirements` quantificados, com referência às capacidades do
sistema requeridas. `ModelRegistry` com catálogo base (Qwen 2.5 7B,
Phi-3 Mini, All MiniLM L6 v2). Domínio puro, sem dependências de
plataforma.

### Validação

```text
py -3.12 -m pytest -v   →   93 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability + 11 model)
```

### Próximo passo

Continuar a Fase 5 (compatibilidade dos modelos contra o sistema e as
capacidades requeridas).

---

## 2026-09-07 — Capability Engine (compatibilidade) — Fase 4

### Objectivo

Concluir a Fase 4 — Capability Engine com o relatório de
compatibilidade: consolidar a avaliação por capacidade com justificação
textual e fechar o catálogo de capacidades disponíveis.

### Criado

- `src/wsai2/capability/compatibility.py`
- Actualizado `src/wsai2/capability/base.py` (CapabilityCompatibility, CompatibilityReport)
- Actualizado `src/wsai2/capability/__init__.py` (exporta novos tipos e build_compatibility)
- `tests/test_capability_compatibility.py`
- `docs/capability/BASE-10-capability-engine-compatibility.md`

### Arquitectura abrangida

Fase 4 — Capability Engine. Subsistema 3.4 da arquitectura.
Relatório consolidado que fecha todos os itens do roadmap da fase
(definições, registo, avaliação, compatibilidade, capacidades
disponíveis).

### Resultado

`build_compatibility` devolve um `CompatibilityReport` com uma
`CapabilityCompatibility` por capacidade registada: estado,
`justification` em linguagem natural (exigido vs disponível) e
agrupamentos available/restricted/unavailable — o catálogo final.

### Validação

```text
py -3.12 -m pytest -v   →   82 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 33 capability)
```

### Próximo passo

Iniciar a Fase 5 — Model Intelligence (subsistema 3.5): registo de
modelos, metadados, requisitos, classificação e recomendação.

---

## 2026-09-07 — Capability Engine (avaliação) — Fase 4

### Objectivo

Implementar a avaliação das capacidades contra o hardware estrutural
(`HardwareProfile`) e o estado do runtime (`RuntimeProfile`), distinguindo
*Hardware Capability* de *Runtime State* e preparando a compatibilidade
e o catálogo de capacidades disponíveis.

### Criado

- `src/wsai2/capability/evaluation.py`
- Actualizado `src/wsai2/capability/base.py` (CapabilityState, RequirementCheck, CapabilityVerdict)
- Actualizado `src/wsai2/capability/__init__.py` (exporta novos tipos e funções)
- `tests/test_capability_evaluation.py`
- Correggido `tests/test_runtime.py` (cpu_percent de processos pode exceder 100% em Windows)
- `docs/capability/BASE-09-capability-engine-evaluation.md`

### Arquitectura abrangida

Fase 4 — Capability Engine. Subsistema 3.4 da arquitectura.
Avaliação com veredictos disponível/condicionada/indisponível e
verificações por requisito, respeitando a separação entre capacidade de
hardware e estado do runtime (Artigo 5 da Constituição).

### Resultado

`evaluate_capability`, `evaluate_capabilities` e `available_capabilities`
devolvem `CapabilityVerdict` com `CapabilityState` e `RequirementCheck`
por requisito (ram_total, ram_available, cpu_cores, gpu, disk). Falha
estrutural → UNAVAILABLE; falha de runtime → RESTRICTED; caso contrário
→ AVAILABLE.

### Validação

```text
py -3.12 -m pytest -v   →   70 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 21 capability)
```

### Próximo passo

Continuar a Fase 4 (compatibilidade: relatório consolidado por
capacidade, fechando o catálogo de capacidades disponíveis).

---

## 2026-09-07 — Capability Engine (definições e registo) — Fase 4

### Objectivo

Iniciar a Fase 4 — Capability Engine com as definições de capacidade e
o registo central, base declarativa para a avaliação e para as
capacidades disponíveis.

### Criado

- `src/wsai2/capability/base.py`
- `src/wsai2/capability/registry.py`
- `src/wsai2/capability/__init__.py`
- `tests/test_capability.py`
- `docs/capability/BASE-08-capability-engine-definitions.md`

### Arquitectura abrangida

Fase 4 — Capability Engine. Subsistema 3.4 da arquitectura.
Determina as capacidades reais que o sistema consegue disponibilizar.

### Resultado

`CapabilityDefinition` com `CapabilityRequirements` quantificados e
`CapabilityRegistry` com catálogo base (inferência local, embeddings,
ML acelerado, processamento leve). Domínio puro, sem dependências de
plataforma.

### Validação

```text
py -3.12 -m pytest -v   →   60 passed (3 fundação + 5 platform + 17 hardware + 24 runtime + 11 capability)
```

### Próximo passo

Continuar a Fase 4 (avaliação das capacidades contra hardware e runtime,
compatibilidade, capacidades disponíveis).

---

## 2026-09-07 — Runtime Intelligence (disponibilidade efectiva) — Fase 3

### Objectivo

Concluir a Fase 3 — Runtime Intelligence com a análise derivada de
disponibilidade efectiva: até que ponto os recursos estão livres para
trabalho no momento da amostragem.

### Criado

- `src/wsai2/runtime/availability.py`
- Actualizado `src/wsai2/runtime/base.py` (AvailabilityDomain, AvailabilityStatus, RuntimeAvailability, RuntimeProfile expandido)
- Actualizado `src/wsai2/runtime/factory.py` (integra analyze_runtime_availability)
- Actualizado `src/wsai2/runtime/__init__.py` (exporta novos tipos)
- `tests/test_runtime.py` (expandido com 10 testes)
- `docs/runtime/BASE-07-runtime-availability.md`

### Arquitectura abrangida

Fase 3 — Runtime Intelligence. Subsistema 3.3 da arquitectura.
Conclui *Runtime State* com avaliação derivada de disponibilidade,
distinta de *Hardware Capability* (Artigo 5 da Constituição).

### Resultado

`RuntimeProfile` completo com 2 disponibilidades (cpu, memory), scores
0.0–1.0, estados HEALTHY–CRITICAL, `overall_status` ponderado,
acessores de conveniência e resumo textual de disponibilidade.

### Validação

```text
py -3.12 -m pytest -v   →   49 passed (3 fundação + 5 platform + 17 hardware + 24 runtime)
```

### Próximo passo

Iniciar Fase 4 — Capability Engine (definições de capacidade, registo,
avaliação, compatibilidade, capacidades disponíveis).

---

## 2026-09-07 — Runtime Intelligence (estado de execução) — Fase 3

### Objectivo

Iniciar a Fase 3 — Runtime Intelligence com o estado de execução do
sistema: carga de CPU, utilização de memória, processos activos e
tempo de actividade, mantendo-o separado da capacidade estrutural.

### Criado

- `src/wsai2/runtime/base.py`
- `src/wsai2/runtime/cpu.py`
- `src/wsai2/runtime/memory.py`
- `src/wsai2/runtime/processes.py`
- `src/wsai2/runtime/factory.py`
- `src/wsai2/runtime/__init__.py`
- `tests/test_runtime.py`
- `docs/runtime/BASE-06-runtime-intelligence.md`

### Arquitectura abrangida

Fase 3 — Runtime Intelligence. Subsistema 3.3 da arquitectura.
Representa *Runtime State* — distinto de *Hardware Capability*
(Artigo 5 da Constituição).

### Resultado

`discover_runtime()` devolve um `RuntimeProfile` com `CpuLoad`,
`MemoryRuntime`, top de processos por memória RSS e `SystemUptime`,
tudo via psutil cross-platform com resumos textuais de apresentação.

### Validação

```text
py -3.12 -m pytest -v   →   39 passed (3 fundação + 5 platform + 17 hardware + 14 runtime)
```

### Próximo passo

Continuar a Fase 3 (análise de disponibilidade efectiva / health checks)
ou fechar a base e avançar para a Fase 4 — Capability Engine.

---

## 2026-09-07 — Hardware Intelligence (perfil e capacidades) — Fase 2

### Objectivo

Concluir a Fase 2 — Hardware Intelligence com perfil de hardware agregado
e capacidades estruturais derivadas (scoring, níveis, nível global).

### Criado

- `src/wsai2/hardware/profile.py`
- Actualizado `src/wsai2/hardware/base.py` (CapabilityLevel, CapabilityDomain, HardwareCapability, HardwareProfile expandido)
- Actualizado `src/wsai2/hardware/factory.py` (integra analyze_hardware_profile)
- Actualizado `src/wsai2/hardware/__init__.py` (exporta novos tipos)
- `tests/test_hardware.py` (expandido com 9 testes)
- `docs/hardware/BASE-05-hardware-profile-capabilities.md`

### Arquitectura abrangida

Fase 2 — Hardware Intelligence. Subsistema 3.2 da arquitectura.
Conclui *Hardware Capability* com análise derivada quantificada.

### Resultado

`HardwareProfile` completo com 4 capacidades (compute, memory, graphics, storage),
scores 0.0–1.0, níveis MINIMAL–HIGH_END, `overall_level` ponderado,
acessores de conveniência, resumos textuais para todos os domínios.

### Validação

```text
py -3.12 -m pytest -v   →   25 passed (3 fundação + 5 platform + 17 hardware)
```

### Próximo passo

Iniciar Fase 3 — Runtime Intelligence (recursos disponíveis, carga, processos, estado de execução).

---

## 2026-09-07 — Hardware Intelligence (GPU e armazenamento) — Fase 2

### Objectivo

Implementar a camada de abstração de plataforma (Platform Foundation) com
detecção de sistema operativo, adaptadores Windows/Linux e fábrica de
seleção, conforme Fase 1 do roadmap.

### Criado

- `src/wsai2/platform/__init__.py`
- `src/wsai2/platform/base.py`
- `src/wsai2/platform/windows.py`
- `src/wsai2/platform/linux.py`
- `src/wsai2/platform/factory.py`
- `tests/test_platform.py`
- `docs/platform/BASE-02-platform-foundation.md`

### Arquitectura abrangida

Fase 1 — Platform Foundation. Subsistema 3.1 da arquitectura. Isola
código específico de SO e expõe interface uniforme via `get_platform()`.

### Resultado

Plataforma detectada correctamente no Windows actual; adaptador Linux
presente e testável; fábrica selecciona adaptador adequado ao SO
corrente.

### Validação

```text
py -3.12 -m pytest -v   →   8 passed (3 fundação + 5 platform)
```

### Próximo passo

Iniciar Fase 2 — Hardware Intelligence (descoberta de CPU, memória,
GPU, armazenamento).

---

## 2026-09-07 — Fundação Python e base de testes

### Objectivo

Estabelecer a infraestrutura Python mínima do projecto e a configuração
inicial da base de testes, tornando verificável cada unidade futura.

### Criado

- `pyproject.toml`
- `src/wsai2/__init__.py`
- `src/wsai2/version.py`
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_foundation.py`
- `docs/foundation/BASE-01-fundacao-python-testes.md`
- `.gitignore`

### Arquitectura abrangida

Fase 0 — Fundação e Governação. Cria o pacote raiz `wsai2` e a base de
testes. Não implementa nenhum subsistema funcional.

### Resultado

Projecto Python instalável em modo editável e base de testes a funcionar.

### Validação

```text
py -3.12 -m pytest -v   →   3 passed
```

### Próximo passo

Concluir os restantes itens da Fase 0 (política de modelos OpenCode e
workflow de sincronização Git) ou iniciar a Fase 1 — Platform Foundation.

---

## 2026-09-07 — Inicialização do projecto

### Objectivo

Estabelecer a primeira base documental e de governação para o desenvolvimento do WorkStation AI 2.

### Criado

- `README.md`
- `AGENTS.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/CONSTITUTION.md`
- `docs/project/ROADMAP.md`
- `docs/project/PROJECT_STATE.md`
- `docs/project/IMPLEMENTATION_LOG.md`

### Arquitectura abrangida

Esta unidade estabelece as regras que irão governar todos os subsistemas futuros. Ainda não implementa Hardware Intelligence, Runtime Intelligence ou qualquer motor funcional.

### Resultado

A fundação documental inicial está estabelecida.

### Próximo passo

Implementar a camada de governação OpenCode:

1. skill central;
2. comando `/wsai-run`;
3. política de modelos;
4. workflow de sincronização Git.

### Validação

Os ficheiros foram criados no repositório remoto oficial.
