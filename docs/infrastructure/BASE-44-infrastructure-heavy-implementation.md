# WORKSTATION AI 2 — RELATÓRIO DA BASE: INFRASTRUCTURE (IMPLEMENTAÇÃO PESADA)

## O que foi feito

Criado o subsistema `wsai2.infrastructure` na unidade **KERNEL-09 — Core
freeze**: reúne a implementação pesada que desceu do núcleo (a mecânica de
execução e governação), por trás dos contratos públicos. A descida moveu
para aqui:

- `base_resource.py` (tipos de governação de recursos) e `governor.py`
  (livro de alocações/reservas, thread-safe);
- `base_runtime.py` (tipos/relatórios do runtime), `manager.py`
  (RuntimeManager), `scheduler.py`, `queue.py` e `monitoring.py`
  (agendamento, filas multicamadas e colecção de métricas).

Os pacotes `wsai2.resource` e `wsai2.runtime_engine` passaram a **shells de
re-export**: mantêm a superfície versionada (KERNEL-05/06) e o `__all__`
congelado, sem implementação residente.

## Onde se encaixa na arquitectura

- Camada de **infra-estrutura** entre o kernel e o domínio (contrato do
  `COMMAND_EXECUTION_CONTRACT`): a infra-estrutura só alcança contratos/
  portos definidos, nunca aplicações nem addons.
- Direcção de dependências: `resource → infrastructure` e
  `runtime_engine → infrastructure`; `infrastructure → {core, execution,
  security, task, hardware, runtime, extension}`. Sem ciclos (o runner de
  `execution` permanece no núcleo — descer criaria `execution ⇄ infra`).
- Não é uma superfície de contrato: sem versão nem `__all__` sancionado.
  As superfícies versionadas permanecem nos pacotes do kernel.

## Para que serve

- Cumprir o critério de qualidade do kernel "a implementação pesada ocorre
  por trás dos contratos públicos, sem residir no núcleo" (sec. 11 do
  `CORE_KERNEL_TARGET.md`).
- Isolar drive de mecânica de execução de qualquer consumidor: nenhum
  módulo fora do kernel pode importar `wsai2.infrastructure` internos.

## Fronteiras (KERNEL-09)

O firewall de dependências (fonte única `tests/architecture_contracts.py`)
registou a nova aresta `(infrastructure, …)` e reduziu `resource` e
`runtime_engine` ao destino `infrastructure`. O teste
`test_implementacao_pesada_fora_do_nucleo` garante que os pacotes do kernel
contêm apenas `__init__.py`.

## Game não alterado

Nenhuma superfície pública, versão ou comportamento mudou: todos os
consumidores importam ao nível do pacote (`wsai2.resource`,
`wsai2.runtime_engine`), por isso a suíte completa permanece verde.