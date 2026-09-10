"""Camada de infra-estrutura da implementação pesada do kernel (KERNEL-09).

Reúne, **por trás** dos contratos públicos, a mecânica de execução e de
governação que a reconstrução do Core extraiu do núcleo: executores de
políticas de execução, governação de recursos, gestor de execução,
agendamento, filas multicamadas e colecção de métricas.

Este pacote **não é uma superfície de contrato**: não possui versão nem
`__all__` sancionado. As superfícies versionadas permanecem nos pacotes do
kernel (`wsai2.resource`, `wsai2.runtime_engine`), que re-exportam daqui.
Pela constituição, a infra-estrutura só alcança contratos/portos definidos,
nunca aplicações nem addons.
"""

from . import (
    base_resource,
    base_runtime,
    governor,
    manager,
    monitoring,
    queue,
    scheduler,
)