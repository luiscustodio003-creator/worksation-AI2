"""Subsistema de extensões do WorkStation AI 2.

Define o contrato mínimo declarativo das extensões (8.1) e, na unidade
8.6, os mecanismos de ciclo de vida (hardening 02) e de compatibilidade
de contratos (hardening 08): máquina de transições de lifecycle,
registo de extensões e versão de contrato ``major.minor`` com rejeição
de incompatibilidades antes do registo/execução.
"""

from .base import (
    ExtensionContract,
    ExtensionKind,
    ExtensionLifecycleState,
    ResourceLimit,
)
from .lifecycle import can_transition, transition, valid_transitions
from .registry import ExtensionRegistry
from .versioning import SUPPORTED_CONTRACT_VERSION, ContractVersion

# Versão do contrato de addon (KERNEL-10): a superfície deste pacote, tal como
# exposta em ``__all__``, está congelada e versionada. Os autores de addons
# devem importar apenas de ``wsai2.extension`` (nível do pacote) e respeitar
# esta versão.
EXTENSION_CONTRACT_VERSION = "1.0"

__all__ = [
    "ContractVersion",
    "ExtensionContract",
    "ExtensionKind",
    "ExtensionLifecycleState",
    "ExtensionRegistry",
    "ResourceLimit",
    "SUPPORTED_CONTRACT_VERSION",
    "can_transition",
    "transition",
    "valid_transitions",
]
