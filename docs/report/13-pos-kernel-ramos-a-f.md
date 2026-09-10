# WORKSTATION AI 2 — PÓS-KERNEL

## A CONSOLIDAÇÃO DO NÚCLEO E OS RAMOS DE DESENVOLVIMENTO A–F

**Estado actual:** Kernel CONSOLIDADO e FROZEN; **Ramo A — Application/Use-Cases** em curso (APP-01..APP-04 congeladas; APP-05 em implementação).
**Referência:** `docs/validation/KERNEL_CONSOLIDATION_REPORT.md`, `docs/project/RUN_GOVERNANCE.md`

---

## 1. O MARCO: KERNEL CONSOLIDADO / FROZEN

Depois das Fases 0–8, o núcleo passou por uma **transição controlada** — a sequência KERNEL-01..KERNEL-10 — para garantir as três propriedades que a visão exige do Core:

1. **pequeno** — conteúdos essenciais (contratos, entidades, invariantes, erros, políticas);
2. **rápido e previsível** — sem implementações pesadas no caminho crítico;
3. **estável** — superfícies públicas **congeladas e versionadas**.

### A sequência KERNEL

```text
KERNEL-01  Inventário real da base
KERNEL-02  Mapa de dependências
KERNEL-03  Core Public Contract          → wsai2.core.public (contrato versionado)
KERNEL-04  Dependency Firewall           → firewall exacto por subsistema
KERNEL-05  Resource/Execution boundary   → superfícies versionadas
KERNEL-06  Observability boundary        → runtime_engine versionado
KERNEL-07  Architecture contract tests   → fonte única de verdade
KERNEL-08  Import migration via core.public
KERNEL-09  Core freeze                   → implementação pesada em wsai2.infrastructure
KERNEL-10  Addon contract freeze          → EXTENSION_CONTRACT_VERSION "1.0"
```

**Resultado:** suíte **506/506 verdes** no fecho da consolidação; contrato de addon congelado; implementação pesada (governor, manager, scheduler, filas, monitorização) desceu para `wsai2.infrastructure` por trás dos contratos. O desenvolvimento normal **não reabre o Kernel** para novas capacidades.

---

## 2. O MODELO DE RAMOS (PÓS-KERNEL)

Com o Kernel congelado, o desenvolvimento passa a avançar por **ramos e unidades**:

```text
A — APPLICATION / USE CASES        READY
B — API / DOMAIN RESOURCES         depende de Application
C — UI                             depende de API / Application
D — KNOWLEDGE SEMANTIC             decisão material / gate próprio
E — ADDON ECOSYSTEM                depende de contratos públicos
F — PROJECTS ADDON                 addon / dependency gate
```

Cada unidade percorre o ciclo:

```text
AUDIT → PLAN → ARQ → IMPLEMENT → TEST → VALIDATE → DOC → GIT → FREEZE
```

Quando a última unidade do ramo termina: `BRANCH COMPLETE → BRANCH FROZEN → DEPENDENCY GATE → NEXT READY BRANCH`.

### Ramo A — Application / Use-Cases (ACTIVO)

```text
APP-01  Audit Application Boundary       ✓ CONCLUÍDA (auditoria read-only)
APP-02  Use-Case Contracts               ✓ CONCLUÍDA (congelada)
APP-03  System / Platform                ✓ CONCLUÍDA (SystemInfoService)
APP-04  Hardware                         ✓ CONCLUÍDA (HardwareProfileService)
APP-05  Runtime
APP-05  Runtime
APP-06  Capabilities
APP-07  Models
APP-08  Tasks
APP-09  Knowledge
APP-10  Execution / Status / Cancellation
APP-11  Application Integration Gate
```

A camada Application define a **fronteira estável dos use-cases** — mensagens puras de pedido/resposta por área, reutilizando os tipos públicos de domínio. **Não contém** lógica central de negócio. No estado actual: APP-02 congelada com o contrato `wsai2.application.contract` (20 mensagens para as 8 áreas: System, Hardware, Runtime, Capabilities, Models, Tasks, Knowledge, Execution/Status/Cancellation) e APP-03 congelada com o adaptador do use-case de informação do sistema (`system.py`, `SystemInfoService`).

### Ramo B — API

Recursos de domínio expostos por unidades: System, Hardware, Runtime, Capabilities, Models, Tasks, Knowledge, Execution/Status + gate de integração. Constrói sobre os contratos de Application e a fundação `wsai2.api` (API-01).

### Ramo C — UI

Dashboard, hardware, modelos, capacidades, tarefas, runtime, conhecimento, execução/estado + gate. Apresenta a informação real da Application/API (artigo 7).

### Ramo D — Knowledge Semantic

O **enriquecimento semântico** (embeddings via Model/Provider) é a decisão material terminal da Fase 9. Ficou registado como ramo próprio com gate independente:

```text
KNOW-SEM-01  Architecture Decision
KNOW-SEM-02  Model / Provider Design
KNOW-SEM-03  Embedding Contract
KNOW-SEM-04  Implementation
KNOW-SEM-05  Persistence / Index Strategy
KNOW-SEM-06  Validation Gate
```

Não se inicia sem decisões documentadas (modelo/fornecedor, integração Provider/Runtime, aditividade sobre o índice lexical).

### Ramo E — Addon Ecosystem

Descobrir, admitir e gerir addons com ciclo de vida, compatibilidade, permissões e requisitos de recursos — usando o contrato de addon congelado no KERNEL-10:

```text
ADDON-01  Discovery
ADDON-02  Admission
ADDON-03  Lifecycle
ADDON-04  Compatibility
ADDON-05  Permissions
ADDON-06  Resource Requirements
ADDON-07  Integration Gate
```

### Ramo F — Projects Addon

O **primeiro consumidor real** do contrato de addon: projectos com estado, isolamento, integração com Knowledge e com skills/comandos.

```text
PROJECT-01  Project Contract
PROJECT-02  Project State / Isolation
PROJECT-03  Project Knowledge Integration
PROJECT-04  Skills / Commands Integration
PROJECT-05  Project Integration Gate
```

---

## 3. DEPENDÊNCIAS ENTRE RAMOS

```text
APPLICATION ────► API ────► UI
     │
     ├──────────► PROJECTS
     │
     └──────────► ADDON ECOSYSTEM

KNOWLEDGE SEMANTIC ──► ADDONS/consumidores quando aplicável
```

A seta representa uma **dependência impeditiva potencial**, não uma ordem artificial — o `wsai-run` confirma a dependência real pelos contratos, gates e código antes de iniciar o ramo seguinte.

---

## 4. CONEXÃO COM A VISÃO

>A visão diz: "queremos um núcleo pequeno, sólido e previsível sobre o qual possam crescer addons especializados" e "o Core não deve depender de Ollama, llama.cpp ou APIs concretas".

O pós-Kernel é a prova operacional dessa filosofia: com o núcleo congelado, a capacidade de crescer transfere-se para **camadas periféricas governadas** (Application, API, UI, addons) — o sistema cresce sem destruir o núcleo.

---

## 5. EVIDÊNCIA E VALIDAÇÃO

- `KERNEL_CONSOLIDATION_REPORT.md` — fecho formal com matriz KERNEL-01..10 e 506/506 verdes.
- `APP-01-application-boundary-audit.md` — auditoria read-only da fronteira Application (85 ficheiros/16 subsistemas no inventário da altura).
- `BASE-46-application-use-case-contracts.md` — contratos de use-case (APP-02, em implementação); suíte actual **528/528 verdes**.
- `RUN_STATE.md` — estado operacional do run por ramo, unidade e etapa.

---

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. O núcleo foi consolidado e **congelado** através da sequência KERNEL-01..10: contrato público, firewall de dependências, superfícies versionadas e implementação pesada fora do núcleo.
2. A partir daqui o desenvolvimento avança por **ramos** (A–F), não por fases abertas.
3. Ramo A (activo): Application — contratos de use-case que tipam o que o núcleo já produz; sem lógica de decisão.
4. Ramo D é o mais delicado: o enriquecimento semântico (embeddings) tem decisão material própria.
5. Ramos E e F concretizam a visão do ecossistema: addons com ciclo de vida, compatibilidade e permissões, crescendo sobre o Core sem o modificar.