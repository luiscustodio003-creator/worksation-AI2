# WORKSTATION AI 2 — RELATÓRIO DA BASE: HARDWARE INTELLIGENCE (CPU E MEMÓRIA)

## O que foi feito

Implementou-se a unidade inicial do subsistema **Hardware Intelligence**
(Fase 2 do roadmap), composta pela descoberta de CPU e memória do
sistema, com normalização cross-platform (Windows/Linux) e contratos
estáveis definidos em `base.py`.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.2 Hardware Intelligence** descrito em
`docs/architecture/ARCHITECTURE.md`. Descobre e descreve CPU, memória,
GPU, armazenamento e características relevantes do sistema. Representa
*Hardware Capability* (capacidade estrutural) — distinto de *Runtime
State* (estado momentâneo de execução, que pertence à Fase 3).

## Para que serve

- Permitir que o resto da aplicação descubra as capacidades estruturais
  de hardware através de `wsai2.hardware.discover_hardware()`.
- Fornecer `CpuInfo` (vendor, modelo, arquitectura, cores físicos/lógicos,
  frequência máxima, cache, features) e `MemoryInfo` (total, swap).
- Isolar a lógica de descoberta concreta (psutil, /proc/cpuinfo) dos
  consumidores, através de contratos (`HardwareDiscoverer` protocol).
- Preparar a base para GPU, armazenamento e perfil de hardware completo.

## Ficheiros criados

- `src/wsai2/hardware/__init__.py` — interface pública do módulo
- `src/wsai2/hardware/base.py` — contratos, enums, dataclasses (`CpuInfo`, `MemoryInfo`, `GpuInfo`, `StorageInfo`, `HardwareProfile`), protocol `HardwareDiscoverer`
- `src/wsai2/hardware/cpu.py` — descoberta de CPU normalizada (psutil + /proc/cpuinfo)
- `src/wsai2/hardware/memory.py` — descoberta de memória normalizada (psutil)
- `src/wsai2/hardware/factory.py` — fábrica `discover_hardware()` que agrega o perfil
- `tests/test_hardware.py` — 7 testes de CPU, memória e integração

## Dependências

- `psutil>=5.9` (adicionado a `pyproject.toml` como dependência de runtime)
- Python ≥ 3.10 (módulos padrão `platform`, `re`, `dataclasses`, `typing`)
- `src/wsai2.platform` — para futuras especializações por SO

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **15 testes aprovados** (3 fundação + 5 platform + 7 hardware).

Os testes validam:
- Estrutura válida de `CpuInfo` e `MemoryInfo`
- Detecção correcta de hyperthreading
- Agregação coerente em `HardwareProfile`
- Resumos textuais não vazios
- Enums de vendor/arquitectura com valores conhecidos

## Estado da fase

**Fase 2 — Hardware Intelligence** — unidade inicial (CPU e memória) concluída.

Restam na Fase 2: descoberta de GPU, armazenamento, perfil de hardware
completo e capacidades estruturais derivadas.

## Próximo passo

Continuar a Fase 2 — Hardware Intelligence com descoberta de GPU e
armazenamento, ou iniciar a Fase 3 — Runtime Intelligence (recursos
disponíveis, carga, processos, estado de execução).