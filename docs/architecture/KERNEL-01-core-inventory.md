# KERNEL-01 — CORE INVENTORY (auditoria de base)

**Data:** 2026-09-09
**Branch:** core-hardening-foundation (fundida com `main`)
**Modo:** `/wsai-audit KERNEL-01`
**Estado arquitectura:** TRANSITION (CORE_KERNEL_TARGET vigente)
**Código alterado:** nenhum (auditoria read-only)

## 1. Âmbito

Inventário real da base antes de qualquer reorganização do Kernel,
conforme `docs/architecture/CORE_KERNEL_TARGET.md` (secção 12, KERNEL-01).
Fonte: código (`src/wsai2`) + testes + docstrings, não suposições.

## 2. Módulos existentes

79 ficheiros Python / 14 subsistemas:

| Subsistema | Responsabilidade | Ficheiros |
|---|---|---|
| `core` | Núcleo transversal: erros + contexto de execução | 3 |
| `execution` | Políticas de execução (contratos + motores) | 3 |
| `resource` | Governação de recursos (accounting, concorrência) | 3 |
| `runtime_engine` | Gestor de execução, scheduler, filas, monitorização | 6 |
| `security` | Política + isolamento de projectos | 4 |
| `platform` | Isolamento Windows/Linux (adaptadores de SO) | 6 |
| `hardware` | Capacidade estrutural (CPU/GPU/memória/storage) | 8 |
| `runtime` | Estado efectivo (CPU/memória/processos/availability) | 7 |
| `capability` | Capacidades: registo, avaliação, compatibilidade | 5 |
| `model` | Modelos: registo, classificação, compatibilidade, recomendação | 6 |
| `provider` | Fornecedores: detecção, probes, health, transports, adaptadores | 8 |
| `task` | Tarefas: contrato, requisitos, classificação, selecção, plano | 6 |
| `extension` | Contratos addon: contrato, lifecycle, versioning, registo | 5 |
| `knowledge` | Knowledge Engine 9.1–9.7 (contrato→registo→metadados→índice→SQLite→contexto→ingestão) | 9 |

## 3. Classificação por destino arquitectural

- **Kernel (Core):** `core`, `execution`, `resource`, `runtime_engine`, `security`.
- **Infraestrutura:** `platform` (adaptadores de SO; isolado pela Constituição).
- **Subsistemas de domínio:** `hardware`, `runtime`, `capability`, `model`, `provider`, `task`, `knowledge`.
- **Contratos addon:** `extension` (+ ponte de grants `extension→security` autorizada).
- **Application (API/UI/CLI):** nenhum — `SUBSISTEMAS_FUTUROS = ("api", "ui")`.
- **Addons futuros (por desenho, fora do core):** PDF/OCR/vision/áudio/embeddings/vector/Projects.

## 4. Dependências (22 arestas autorizadas — `FRONTEIRAS`)

`capability→hardware/runtime`; `core→extension`; `execution→core/resource`;
`extension→core/security`; `knowledge→core`; `model→capability/hardware/runtime`;
`resource→core/extension/hardware/runtime`; `runtime_engine→core/execution/resource/security/task`;
`security→core`; `task→capability/hardware/model/provider/runtime`.

Grafo de imports **acíclico** em runtime (verificado por testes com
`TYPE_CHECKING` excluído).

## 5. Consumidores (scan AST real)

- `execution` ← `runtime_engine.{manager,scheduler}`
- `resource` ← `runtime_engine.manager`; `resource.governor` consome `extension`+`hardware`
- `extension` ← `resource.governor`; `extension→security` (ponte de grants)
- `core.*` ← execution, extension, knowledge, resource, runtime_engine, security
- `platform` apenas via fábricas de hardware/runtime

## 6. Testes

481 testes de domínio + 10 de contrato arquitectural = **491/491 verdes**
(gate real 2026-09-09, `exit 0`), na linha fundida. Zero violações de
fronteiras; subsistemas futuros não antecipados.

## 7. Problemas

- **P3 — ABERTO:** `core.public`/`core.internal` não materializados (decisão: só após inventário; KERNEL-03).
- **P3 — ABERTO:** observabilidade transversal sem contrato (monitorização contínua existe sem API pública de métricas).
- **P3 — ATENÇÃO:** `runtime_engine` é o nó mais concêntrico (5 arestas de saída) — maior raio de impacto.
- **P3 — INFORMATIVO:** `resource.governor→hardware` será reavaliado na definição do `core.public`.

## 8. Riscos de migração

- **R1 — MÉDIO:** criar `core.public`/`core.internal` sem inventário — mitigado por este documento.
- **R2 — MÉDIO:** alterações em `runtime_engine.{manager,scheduler,queue}` têm o maior raio de impacto.
- **R3 — BAIXO:** `platform.*` e `*.base` não saem do próprio subsistema.
- **R4 — BAIXO:** mover a ponte `extension→security` pode regredir grants (testada por contrato).
- **R5 — INFORMATIVO:** a ingestão 9.7 e o fecho da Fase 9 estão integrados nesta linha — não reverter.

## 9. Recomendação

PRÓXIMA UNIDADE — `/wsai-plan KERNEL-02`: mapa de dependências formal +
proposta de fronteiras públicas (`core.public`), evitando MOVE físico
antes do contrato. Risco MÉDIO, sem bloqueadores P0/P1/P2.