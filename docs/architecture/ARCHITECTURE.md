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

Executa planos, gere recursos, concorrência, cancelamento, timeouts, streaming e observabilidade.

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

As fases Platform Foundation, Hardware Intelligence, Runtime Intelligence, Capability Engine, Model Intelligence, Provider Layer e Task Intelligence encontram-se concluídas. A **Fase 8 — Runtime Engine** está em curso: concluídas as unidades 8.1 (Extension Contract, contrato mínimo declarativo de extensões) e 8.2 (Execution Context + Error Model, camada transversal `wsai2.core`).

A fonte de verdade para o progresso e a próxima unidade é `docs/project/PROJECT_STATE.md`.
