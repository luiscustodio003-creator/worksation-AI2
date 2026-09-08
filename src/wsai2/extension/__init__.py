"""Subsistema de extensões do WorkStation AI 2.

Responsável por definir o contrato mínimo declarativo das extensões
(addons) do sistema (hardening 01 do CORE_HARDENING_PLAN).

Nesta unidade da Fase 8 é implementado apenas o **contrato de extensão**:
tipos de extensão, estados de lifecycle e o contrato imutável com
identidade, versões, capacidades, dependências, recursos, permissões e
metadados. O registo, o gestor e o ciclo de execução pertencem a
unidades posteriores da Fase 8.
"""

from .base import (
    ExtensionContract,
    ExtensionKind,
    ExtensionLifecycleState,
    ResourceLimit,
)

__all__ = [
    "ExtensionContract",
    "ExtensionKind",
    "ExtensionLifecycleState",
    "ResourceLimit",
]
