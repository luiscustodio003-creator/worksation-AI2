# WORKSTATION AI 2 — RELATÓRIO DA BASE: HARDWARE INTELLIGENCE (GPU E ARMAZENAMENTO)

## O que foi feito

Implementou-se a continuação do subsistema **Hardware Intelligence**
(Fase 2 do roadmap), adicionando descoberta de GPU e armazenamento
com suporte cross-platform (Windows via WMI, Linux via lspci/sysfs)
e fallbacks graciosos.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.2 Hardware Intelligence** descrito em
`docs/architecture/ARCHITECTURE.md`. Completa a descoberta de
capacidades estruturais de hardware: CPU, memória, GPU, armazenamento.
Representa *Hardware Capability* — distinto de *Runtime State*.

## Para que serve

- Permite descobrir GPUs (vendor, nome, VRAM, driver version) via
  `wsai2.hardware.discover_gpus()`.
- Permite descobrir dispositivos de armazenamento (device, tamanho,
  tipo SSD/HDD/NVMe, mount point) via `wsai2.hardware.discover_storage()`.
- Integra ambos no `HardwareProfile` devolvido por `discover_hardware()`.
- Isola lógica específica de SO (WMI, lspci, sysfs) atrás de contratos
  estáveis.

## Ficheiros criados

- `src/wsai2/hardware/gpu.py` — descoberta GPU (WMI Windows, lspci/sysfs Linux)
- `src/wsai2/hardware/storage.py` — descoberta armazenamento (psutil + heurísticas)
- Actualizado `src/wsai2/hardware/factory.py` — integra GPU e storage
- Actualizado `src/wsai2/hardware/__init__.py` — exporta novas funções
- `tests/test_hardware.py` — +4 testes (GPU, storage, integração)

## Dependências

- `psutil>=5.9` (já presente)
- `wmi` (opcional, Windows) — para GPU via WMI
- `lspci` (sistema, Linux) — para GPU via PCI
- Ferramentas padrão do SO (sysfs, /proc)

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **17 testes aprovados** (3 fundação + 5 platform + 9 hardware).

Os testes validam:
- Estrutura válida de `GpuInfo` (lista, pode ser vazia)
- Estrutura válida de `StorageInfo` (lista não vazia, campos obrigatórios)
- Agregação coerente em `HardwareProfile` com GPU e storage
- Tipos de disco detectados (ssd, hdd, nvme, usb, unknown)

## Estado da fase

**Fase 2 — Hardware Intelligence** — unidade CPU/memória + GPU/storage concluída.

Restam na Fase 2: perfil de hardware completo e capacidades estruturais derivadas.

## Próximo passo

Completar Fase 2 com perfil de hardware agregado e capacidades estruturais,
ou iniciar Fase 3 — Runtime Intelligence (recursos disponíveis, carga,
processos, estado de execução).