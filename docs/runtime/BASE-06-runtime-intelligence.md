# WORKSTATION AI 2 — RELATÓRIO DA BASE: RUNTIME INTELLIGENCE (ESTADO DE EXECUÇÃO)

## O que foi feito

Foi implementada a primeira unidade da **Fase 3 — Runtime Intelligence**
(subsistema 3.3 da arquitectura): recursos disponíveis, carga de CPU,
processos activos e estado de execução (uptime). Criou-se um novo pacote
`wsai2.runtime` que representa o *Runtime State* (estado momentâneo de
execução), mantendo-o estritamente separado do *Hardware Capability*
(capacidade estrutural descoberta pelo subsistema 3.2).

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.3 Runtime Intelligence** descrito em
`docs/architecture/ARCHITECTURE.md`. A separação fundamental entre
*Hardware Capability* e *Runtime State* (Artigo 5 da Constituição) foi
respeitada: o novo módulo não expande os contratos de hardware e a
capacidade estrutural permanece intacta.

## Para que serve

- Retrata a carga real do CPU no instante da amostragem (`CpuLoad`).
- Retrata a utilização efectiva de memória (`MemoryRuntime`).
- Lista os processos mais relevantes por consumo de memória (`ProcessInfo`).
- Retrata o tempo de actividade do sistema (`SystemUptime`).
- Agrega tudo num `RuntimeProfile` com resumos textuais.

## Ficheiros criados

- `src/wsai2/runtime/base.py` — contratos e tipos
- `src/wsai2/runtime/cpu.py` — descoberta de carga do CPU
- `src/wsai2/runtime/memory.py` — descoberta de utilização de memória
- `src/wsai2/runtime/processes.py` — processos mais relevantes
- `src/wsai2/runtime/factory.py` — agregador `discover_runtime()`
- `src/wsai2/runtime/__init__.py` — interface pública
- `tests/test_runtime.py` — validação

## Dependências

- `psutil>=5.9` (a base já existente)
- Hardware Intelligence (já concluída) para a distinção entre
  capacidade estrutural e estado momentâneo

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **39 testes aprovados** (3 fundação + 5 platform + 17 hardware
+ 14 runtime).

Os testes validam:

- `CpuLoad` bem formado com carga global e por core;
- `MemoryRuntime` coerente (total = disponível + usado, percentagens válidas);
- processos ordenados por memória RSS, com tipos obrigatórios correctos;
- `RuntimeProfile` agregado via `discover_runtime()` (sem exigir windows/Linux);
- uptime retornado correctamente, resumos textuais presentes;
- propriedades booleanas `is_idle`/`is_saturated` e `has_swap_active`.

## Estado da fase

**Fase 3 — Runtime Intelligence** — **EM PROGRESSO**.
Itens do roadmap implementados nesta unidade:

- recursos disponíveis ✓ (memória disponível, carga de CPU)
- carga ✓ (`CpuLoad`, per-core, frequência)
- processos ✓ (`ProcessInfo`, top por memória)
- estado de execução ✓ (uptime não NOP)
- perfil de runtime ✓ (`RuntimeProfile`)

## Próximo passo

Completar a Fase 3 com análise derivada de disponibilidade efectiva
(avaliação/health checks por domínio) e, quando a base estiver fechada,
avançar para a Fase 4 — Capability Engine.