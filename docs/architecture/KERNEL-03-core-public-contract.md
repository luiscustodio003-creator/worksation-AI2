# KERNEL-03 — CORE PUBLIC CONTRACT

**Data:** 2026-09-09
**Branch:** core-hardening-foundation
**Unidade:** KERNEL-03 — contrato público do núcleo
**Decisão:** Opção A — fachada `wsai2.core.public` limitada aos contratos do
leaf `core` (autorizada em planeamento; sem alterações ao firewall)
**Código alterado:** `src/wsai2/core/public.py` (novo) + teste

## 1. Decisão de localização

A Core Public API não pode, nesta fase, ser um agregado único de todos os
módulos do kernel: `core` é camada folha (Artigo 2, `FRONTEIRAS`) e uma
fachada que importasse execution/resource/runtime_engine/security
introduziria ciclos e violaria a aciclicidade. Confirmado o bloqueio em
planeamento. **Opção A adoptada:**

- `core.public` expõe apenas os contratos que já pertencem ao leaf `core`;
- as superfícies de `execution`, `resource`, `runtime_engine` e `security`
  são definidas por unidade de fronteira (KERNEL-05/06), cada uma na sua
  localização, sem romper o firewall;
- a agregação completa para Application/Addons fica para depois da
  migração de imports (KERNEL-08).

## 2. Contrato versionado

```python
CORE_PUBLIC_CONTRACT_VERSION = "1.0"
```

Padrão `major.minor`, espelhando `KNOWLEDGE_CONTRACT_VERSION` (Fase 9.1).
Evolução com compatibilidade explícita; alterações incompatíveis sobem o
`major`.

## 3. Superfície pública (14 símbolos)

### Taxonomia de erros (`core.errors`)

`WsaiError`, `ValidationError`, `CapabilityError`, `ModelError`,
`ProviderError`, `ResourceError`, `TimeoutError`, `CancellationError`,
`PermissionError`, `ProjectIsolationError`, `ExecutionError`.

### Contexto de execução (`core.context`)

`ExecutionContext`, `CancellationToken`, `ExecutionPriority`.

## 4. Garantias (testes)

- Versão "1.0" com formato `major.minor` numérico;
- `__all__` exacto = superfície declarada;
- **identidade** com `wsai2.core` (sem drift/duplicação);
- varredura AST: `core/public.py` só importa do próprio subsistema
  (firewall e folha intactos);
- nenhuma classe/função própria (fachada pura).

## 5. Regressão

Suíte completa: **496/496 verdes** (491 + 5 novos) na linha
`core-hardening-foundation`. `FRONTEIRAS`, aciclicidade e os 10 testes de
contrato arquitectural inalterados.

## 6. O que ficou adiado

- Superfícies públicas de execution/resource/runtime_engine/security →
  KERNEL-05 (Resource/Execution boundary) e KERNEL-06 (Observability
  boundary);
- Divisão física `public`/`internal` → KERNEL-08 (migração incremental de
  imports); `core/public.py` é o primeiro entry-point, sem MOVE.