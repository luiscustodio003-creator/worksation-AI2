# WORKSTATION AI 2 — CORE / EXECUTION & INTELLIGENCE KERNEL

## 1. Objectivo

Este documento define a estrutura-alvo do núcleo do WSAI 2 e a estratégia de reorganização incremental da base existente.

O objectivo **não é reescrever o projecto**. É consolidar as responsabilidades que já existem, tornar as fronteiras explícitas e preparar o Core para addons, Projects, API e UI sem introduzir dependências pesadas no núcleo.

O nome arquitectural recomendado é **Core / Execution & Intelligence Kernel**. No código, a convenção continua a ser `wsai2.core` para o núcleo mínimo e os restantes subsistemas permanecem módulos de domínio do WSAI 2.

## 2. Princípio fundamental

O Core deve ser pequeno, determinista, testável e independente de capacidades concretas.

```text
                APPLICATION
             API / UI / CLI
                    |
                    v
             CORE PUBLIC API
                    |
        +-----------+-----------+
        |           |           |
     DECIDE      PLAN       GOVERN
        |           |           |
        +-----------+-----------+
                    |
                    v
               EXECUTION
                    |
       +------------+-------------+
       |            |             |
   HARDWARE      RUNTIME       MODELS
   CAPABILITY     STATE      / PROVIDERS
       |            |             |
       +------------+-------------+
                    |
                    v
                  ADDONS
```

O diagrama representa responsabilidades e contratos, não necessariamente pacotes Python independentes.

## 3. O que pertence ao núcleo

### 3.1 Core Contracts

**Responsabilidade:** definir os contratos estáveis usados para comunicar com o núcleo.

**Inclui:** contexto de execução, pedidos, planos, resultados, erros, prioridades, orçamento e metadados de execução.

**Dependências:** biblioteca standard e tipos internos estáveis.

**Não inclui:** parsing de documentos, OCR, embeddings, UI, HTTP, runtimes de modelos ou código específico de fornecedor.

**Vantagens:** baixo acoplamento e testes rápidos.

**Limitações:** o contrato deve evoluir com compatibilidade explícita; não deve ser transformado num depósito de funcionalidades.

### 3.2 Decision / Policy Layer

**Responsabilidade:** autorizar e governar a execução com base em projecto, capability, recursos, prioridade e políticas.

**Dependências:** contratos, estado de runtime e informação de capacidades.

**Não deve:** implementar a capability concreta.

### 3.3 Execution Planning

**Responsabilidade:** transformar uma tarefa admitida numa estratégia de execução.

A decisão deve considerar, quando disponível:

```text
Task
+ Project
+ Hardware Capability
+ Runtime State
+ Capability
+ Model
+ Provider
+ Resource Budget
+ Priority
+ Policy
+ Historical Metrics
        |
        v
Execution Plan
```

**Regra:** o addon declara requisitos; não escolhe autonomamente threads, modelo, backend ou orçamento fora do contrato do Core.

### 3.4 Runtime / Execution Governance

**Responsabilidade:** executar o plano e controlar timeout, cancelamento, recursos, concorrência, filas, recovery e observabilidade.

O WSAI 2 já possui a base desta responsabilidade em `wsai2.execution`, `wsai2.resource`, `wsai2.runtime_engine` e `wsai2.security`. A reorganização deve primeiro consolidar as interfaces entre estes módulos; não deve duplicar os mecanismos existentes.

### 3.5 Observability

**Responsabilidade:** tornar a execução observável sem obrigar addons a conhecerem o mecanismo interno de métricas.

Deve permitir, progressivamente:

- duração;
- estado;
- CPU/RAM/VRAM quando disponível;
- falhas;
- timeout/cancelamento;
- modelo/provider;
- addon;
- projecto;
- estratégia seleccionada.

## 4. O que NÃO pertence ao Core

Os seguintes componentes devem ser addons ou infraestrutura especializada:

- PDF/document processing;
- OCR;
- Computer Vision;
- áudio/Whisper;
- embeddings;
- vector stores especializados;
- DOCX/PPTX/PSD;
- scraping/web;
- GitHub-specific processing;
- interfaces Web;
- API HTTP concreta;
- Ollama-specific logic;
- llama.cpp-specific logic;
- modelos concretos;
- bases de dados específicas de uma capability.

O Core pode definir contratos para estas capacidades, mas não deve implementá-las.

## 5. Separação Hardware Capability / Runtime State

Esta separação é obrigatória.

**Hardware Capability** responde: "O que a máquina suporta estruturalmente?"

**Runtime State** responde: "O que está efectivamente disponível agora?"

Um plano deve poder usar ambos sem os confundir.

Exemplo:

```text
Hardware:
  4 cores / 8 threads
  8 GB RAM

Runtime:
  2.1 GB RAM livre
  CPU elevada

Capability:
  modelo X compatível

Resultado:
  modelo X pode ser compatível com a máquina,
  mas pode não ser a escolha adequada neste momento.
```

## 6. Regra de dependências

A direcção desejada é:

```text
Application / UI / API
        |
        v
Core Public Contracts
        |
        +--> Domain subsystems
        |       Hardware
        |       Runtime
        |       Capability
        |       Model
        |       Provider
        |       Knowledge
        |
        +--> Extension contracts

Addons
  |
  +--> Core Public API
  +--> contratos específicos permitidos
  X--> Core internals
  X--> outros addons
  X--> UI/API
```

O Core não importa addons.

Um addon não pode importar outro addon directamente.

Dependências concretas entre subsistemas só são aceites quando justificadas pelo contrato arquitectural e cobertas por testes.

## 7. Superfície pública do Core

A reorganização futura deve distinguir claramente:

```text
wsai2.core.public
    contratos destinados a consumidores externos

wsai2.core.internal
    mecanismos internos do núcleo

wsai2.<subsystem>
    subsistemas de domínio do WSAI 2
```

A introdução física de `public/` e `internal/` só deve ocorrer depois do inventário dos imports existentes. Não se deve mover ficheiros apenas por estética.

## 8. Addon boundary

O ciclo de um addon deve ser:

```text
Addon
  |
  | declara capability + requisitos
  v
Core admission
  |
  | valida contrato / versão / permissões / recursos
  v
Execution Planner
  |
  | produz estratégia
  v
Addon execution
  |
  | devolve resultado/eventos
  v
Core governance + observability
```

Uma falha do addon deve ser isolada e representada através do modelo de erros do Core; não deve derrubar o núcleo.

## 9. Project Addon — integração futura

O futuro addon `Projects` deve consumir o Core, não tornar-se parte do Core.

Cada projecto terá contexto próprio, incluindo, conforme evolução:

- identidade e sigla;
- descrição;
- requisitos;
- arquitectura;
- roadmap;
- decisões;
- estado;
- skill do projecto;
- regras;
- testes;
- documentação.

Os comandos devem ser universais. O contexto do projecto determina o comportamento.

```text
/st-plan
   |
   +--> command = PLAN
   +--> project = ST
   +--> project context
   +--> project skill
   +--> Core

/wsai-plan
   |
   +--> command = PLAN
   +--> project = WSAI
   +--> project context
   +--> project skill
   +--> Core
```

O comando não deve conter lógica específica do projecto.

## 10. Estratégia de reorganização

A migração deve seguir **Preservar antes de estender**:

1. inventariar módulos e imports reais;
2. classificar cada módulo por responsabilidade;
3. identificar dependências actuais;
4. definir fronteiras públicas;
5. criar testes de arquitectura para as fronteiras;
6. introduzir adaptadores/fachadas quando necessários;
7. migrar imports gradualmente;
8. executar a suíte completa após cada unidade;
9. só remover caminhos antigos depois de comprovada a equivalência;
10. actualizar documentação e estado.

Não deve existir uma grande migração única.

## 11. Critérios de qualidade do Kernel

O núcleo será considerado consolidado quando:

- as responsabilidades estiverem explícitas;
- os imports proibidos forem detectáveis automaticamente;
- addons consumirem apenas a superfície pública;
- Hardware Capability e Runtime State permanecerem separados;
- planeamento e governação de recursos permanecerem no núcleo;
- contratos possuírem versão;
- falhas de addons forem isoladas;
- observabilidade for transversal;
- a suíte completa permanecer verde;
- não existirem dependências pesadas desnecessárias no arranque do Core;
- a API e UI puderem evoluir sem modificar a lógica central.

## 12. Primeira sequência de trabalho

```text
KERNEL-01  Inventário real da base          ✓ CONCLUÍDA (KERNEL-01-core-inventory.md)
KERNEL-02  Mapa de dependências             ✓ CONCLUÍDA (KERNEL-02-dependency-map.md)
KERNEL-03  Core Public Contract             ✓ CONCLUÍDA (KERNEL-03-core-public-contract.md)
KERNEL-04  Dependency Firewall              -> próxima unidade
KERNEL-05  Resource / Execution boundary    -> depois
KERNEL-06  Observability boundary            -> depois
KERNEL-07  Architecture contract tests      -> depois
KERNEL-08  Migração incremental de imports  -> depois
KERNEL-09  Core freeze                       -> depois
KERNEL-10  Addon SDK / Projects foundation  -> depois
```

A ordem pode ser alterada apenas após auditoria da unidade anterior e sem contrariar `PROJECT_STATE.md`.

## 13. Regra de ouro

> **O Core decide e governa. O addon fornece a capacidade. O projecto fornece o contexto. O comando fornece a operação. A UI apresenta o estado.**

Esta separação é a base para o WSAI 2 crescer sem transformar o núcleo num monólito.
