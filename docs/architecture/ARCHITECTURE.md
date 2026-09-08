# WORKSTATION AI 2 — ARQUITECTURA

## 1. Objectivo arquitectural

O WorkStation AI 2 será construído como uma plataforma local e multiplataforma de inteligência artificial capaz de compreender o ambiente onde está a executar e tomar decisões sobre capacidades, modelos e execução.

A arquitectura deve permitir evolução em Windows e Linux sem misturar responsabilidades.

## 2. Camadas principais

```text
Interface / UI
      │
API / Presentation
      │
Application Services
      │
Domain / Core
      │
Infrastructure / Providers / Platform
```

As dependências devem apontar para dentro. O domínio não depende da API, da interface ou de fornecedores concretos.

## 3. Subsistemas funcionais

### 3.1 Platform Foundation

Abstrai diferenças entre sistemas operativos e fornece acesso controlado a funcionalidades específicas de Windows e Linux.

### 3.2 Hardware Intelligence

Descobre e descreve CPU, memória, GPU, armazenamento e características relevantes do sistema.

### 3.3 Runtime Intelligence

Representa o estado actual dos recursos: memória disponível, carga de CPU/GPU, processos e disponibilidade efectiva.

### 3.4 Capability Engine

Determina as capacidades reais que o sistema consegue disponibilizar a partir de hardware, runtime, software e fornecedores instalados.

### 3.5 Model Intelligence

Mantém informação sobre modelos, requisitos, compatibilidade, desempenho e adequação às tarefas. A selecção de modelo é independente da escolha do fornecedor.

### 3.6 Provider Layer

Isola os fornecedores e motores concretos, como runtimes locais e APIs compatíveis. O subsistema possui contratos, registo, detecção, adaptadores e health checks. A comunicação externa é feita através de adaptadores e transportes injectáveis.

### 3.7 Task Intelligence

Interpreta tarefas, identifica requisitos e produz planos de execução.

### 3.8 Runtime Engine

Executa planos, gere recursos, concorrência, cancelamento, timeouts, streaming e observabilidade. Inclui o ciclo de vida, o registo e a compatibilidade de extensões: em 8.6, `wsai2.extension.lifecycle` (máquina de transições, pura e sem efeitos laterais — uma falha de addon não derruba o Core), `wsai2.extension.registry` (`ExtensionRegistry`, padrão dos registos das Fases 4–6, com o estado de lifecycle mantido no próprio contrato) e `wsai2.extension.versioning` (`ContractVersion` `major.minor`; compatibilidade por major; rejeição antes do registo/execução). Em 8.8, `wsai2.security` (folha) implementa os hardening 09+10: `PolicyEngine` com decisão exact-match por acção, `denied_decision`/guardas `require_project`/`assert_same_project` (emissores reais da taxonomia da 8.2) e enforcement opcional no `RuntimeManager` antes do passo 1. Em 8.9, o **Gate — Core pronto para addons**: o `Scheduler` propaga a política ao gestor (contrato de composição: quem cria o runtime passa o motor) e o `ExtensionRegistry` materializa `permissions` como grants por id de extensão, com critério executável em `tests/test_gate_addons.py`. Nas unidades residuais Via B, (1) **monitorização contínua** — `wsai2.runtime_engine.monitoring` adiciona observação em curso (thread-safe, `snapshot()`) às execuções e agendamentos, aditiva ao relatório pós-facto e reversível; (2) **concorrência entre planos** — `Scheduler.run` ganha `concurrency` aditivo (sequencial por omissão; paralelo opcional via `ThreadPoolExecutor` com relatório em ordem de prioridade) e o `ResourceGovernor` passa a thread-safe, permitindo partilha segura entre planos paralelos; (3) **filas multicamadas** — `MultilayerExecutionQueue` adiciona filas por prioridade com backlog, capacidade opcional, preempção apenas de trabalho pendente, promoção automática do backlog e operações `snapshot()`/`pending()`/`clear()`, com integração opt-in no `Scheduler.run(queue=...)`. A via directa `queue=None` preserva o comportamento histórico. A implementação está documentada em `docs/runtime_engine/BASE-36-runtime-engine-queues.md`.

### 3.9 Knowledge Engine

Trata a gestão de conhecimento: ingestão de ficheiros, extracção, metadados, indexação, recuperação e construção de contexto. Na unidade 9.1 foi criado o contrato declarativo do subsistema (`wsai2.knowledge`): `KnowledgeKind` (document/extract/note), `KnowledgeMetadata` (fonte, idioma, autor, etiquetas) e `KnowledgeRecord` (imutável, validado à criação), além da versão de contrato `KNOWLEDGE_CONTRACT_VERSION = "1.0"`. O subsistema é **folha** — depende apenas de stdlib; a ingestão e a extracção reais consumirão extensões, fornecedores e o Runtime em unidades posteriores, sem antecipar I/O nem motores de embeddings neste contrato.

### 3.10 API

Expõe capacidades reais do sistema através de contratos estáveis.

### 3.11 UI

Apresenta informação e operações disponibilizadas pela aplicação. Não contém a lógica central de decisão.

## 4. Separação fundamental

### Hardware Capability

Descreve aquilo que a máquina suporta em termos estruturais.

### Runtime State

Descreve os recursos realmente disponíveis no momento da execução.

Estas duas entidades devem permanecer separadas.

## 5. Independência de modelos e fornecedores

O WSAI 2 não deve depender de um modelo, fabricante, repositório, runtime de inferência ou fornecedor específico.

A decisão de **qual modelo usar** e a decisão de **através de que fornecedor o executar** são responsabilidades separadas.

```text
Tarefa
  ↓
Model Intelligence
  ↓
Modelo recomendado
  ↓
Provider Layer
  ↓
Fornecedor compatível e saudável
  ↓
Runtime Engine
```

Um fornecedor concreto deve ser substituível por outro que implemente o contrato adequado sem exigir alterações no domínio central.

## 6. Fluxo de decisão futuro

```text
Pedido
  ↓
Task Intelligence
  ↓
Requisitos
  ↓
Capability Engine
  ↓
Model Intelligence
  ↓
Provider Layer
  ↓
Execution Plan
  ↓
Runtime Engine
  ↓
Resultado
```

## 7. Estado actual da arquitectura

As fases Platform Foundation, Hardware Intelligence, Runtime Intelligence, Capability Engine, Model Intelligence, Provider Layer, Task Intelligence e **Fase 8 — Runtime Engine** encontram-se concluídas (8.1–8.9, monitorização contínua, concorrência entre planos e filas multicamadas). A Fase 8 foi **formalmente fechada** pelo gate de validação da fundação (consulta `docs/validation/FOUNDATION_VALIDATION_REPORT.md`).

A **Fase 9 — Knowledge Engine** está em curso: a unidade 9.1 define o contrato declarativo do subsistema 3.9 (`wsai2.knowledge`).

A fonte de verdade para o progresso, estado de validação e próxima fase é `docs/project/PROJECT_STATE.md`. A arquitectura e os planos de hardening devem reflectir o estado real do código e dos testes; não devem manter como “futuro” um componente já implementado e coberto por testes.

### 7.1 Maturidade arquitectural versus conclusão funcional

As percentagens apresentadas em `PROJECT_STATE.md` são indicadores de **maturidade/cobertura arquitectural**, não percentagens de implementação da fase. Assim, uma área pode estar funcionalmente concluída e continuar abaixo de 100% de maturidade por conter espaço para evolução, integração ou hardening posterior.
