"""Contratos e tipos fundamentais do Provider Layer.

Este módulo contém apenas definições de tipos e dataclasses — não
implementa detecção, adaptadores nem health checks. Define o que é um
fornecedor (provider) conhecido pelo sistema e como o declarar.

O *fornecedor* é a entidade central do subsistema 3.6: isola os motores
concretos (runtimes locais e APIs compatíveis) atrás de um contrato
estável. As unidades seguintes detectam a presença do fornecedor,
adaptam a comunicação e verificam a sua saúde.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProviderType(Enum):
    """Tipo de fornecedor segundo a sua natureza de execução."""

    LOCAL_RUNTIME = "local_runtime"  # Motor local no sistema (ex.: Ollama)
    REMOTE_API = "remote_api"        # API remota compatível (ex.: OpenAI)


@dataclass(frozen=True)
class ProviderDefinition:
    """Definição estrutural de um fornecedor conhecido do sistema.

    Representa o contrato declarativo de um fornecedor que o
    WorkStation AI 2 pode usar, incluindo o tipo, o endpoint base
    predefinido e as capacidades do sistema que o fornecedor pode
    disponibilizar.
    """

    id: str
    name: str
    description: str
    type: ProviderType
    default_base_url: str = ""
    capabilities_provided: tuple[str, ...] = field(default_factory=tuple)

    @property
    def summary(self) -> str:
        """Resumo textual do fornecedor para apresentação."""
        return f"{self.name} ({self.id})"


__all__ = [
    "ProviderDefinition",
    "ProviderType",
]