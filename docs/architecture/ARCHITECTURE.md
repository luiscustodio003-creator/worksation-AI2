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

Executa planos, gere recursos, concorrência, cancelamento, timeouts, streaming e observabilidade. Inclui o ciclo de vida, o registo e a compatibilidade de extensões: em 8.6, `wsai2.extension.lifecycle` (máquina de transições, pura e sem efeitos laterais — uma falha de addon não derruba o Core), `wsai2.extension.registry` (`ExtensionRegistry`, padrão dos registos das Fases 4–6, com o estado de lifecycle mantido no próprio contrato) e `wsai2.extension.versioning` (`ContractVersion` `major.minor`; compatibilidade por major; rejeição antes do registo/execução). Em 8.8, `wsai2.security` (folha) implementa os hardening 09+10: `PolicyEngine` com decisão exact-match por acção, `denied_decision`/guardas `require_project`/`assert_same_project` (emissores reais da taxonomia da 8.2) e enforcement opcional no `RuntimeManager` antes do passo 1.

### 3.9 Knowledge Engine

Trata ingestão de ficheiros, extracção, metadados, indexação, recuperação e construção de contexto.

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

As fases Platform Foundation, Hardware Intelligence, Runtime Intelligence, Capability Engine, Model Intelligence, Provider Layer e Task Intelligence encontram-se concluídas. A **Fase 8 — Runtime Engine** está em curso: concluídas as unidades 8.1 (Extension Contract, contrato mínimo declarativo de extensões), 8.2 (Execution Context + Error Model, camada transversal `wsai2.core`), 8.3 (Resource Governance, subsistema `wsai2.resource` com governador de orçamento e accounting de recursos), 8.4 (Execution Policies, subsistema `wsai2.execution` com timeout, cancelamento cooperativo e recuperação centralizados), 8.5 (Runtime Engine, subsistema `wsai2.runtime_engine` com `RuntimeManager` que executa o `ExecutionPlan` do Task Intelligence e `Scheduler` determinístico por prioridade) e 8.6 (Extension Lifecycle + Compatibility, subsistema `wsai2.extension` com máquina de lifecycle pura, `ExtensionRegistry` e `ContractVersion` com compatibilidade por major e rejeição antes do registo), 8.7 (Architecture Contract Tests, testes executáveis das regras da Constituição sobre o repositório — fronteiras de dependências, isolamento de SO, ausência de ciclos de import e documentação por subsistema) e 8.8 (Security/Policy + Project Isolation, subsistema folha `wsai2.security` com `PolicyEngine` exact-match, guardas de projecto e enforcement antes do passo 1 no `RuntimeManager`).

A fonte de verdade para o progresso e a próxima unidade é `docs/project/PROJECT_STATE.md`.
