"""Contratos e tipos fundamentais do Extension Contract.

Este módulo contém apenas definições de tipos e dataclasses — não
implementa registo, gestão, ciclo de execução nem integração com o
Runtime. Define o contrato mínimo comum para extensões/addons do
WorkStation AI 2 (hardening 01 do CORE_HARDENING_PLAN): identidade,
versão, versão do contrato, tipo, capacidades, dependências, recursos,
permissões e estado de lifecycle.

O contrato é declarativo e imutável; serve de base para o Runtime
Engine e para a futura camada de security/policy (hardening 09), sem
acoplar esta unidade a esses subsistemas. As capacidades são referidas
por identificador textual, de modo reversível e sem criar dependência
prematura com o Capability Engine ou o Provider Layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ExtensionKind(Enum):
    """Tipo funcional de uma extensão.

    Estes tipos previstos não são uma lista fechada; representam as
    categorias conhecidas de addons que o WorkStation AI 2 poderá
    albergar. Servem de base à política de segurança (hardening 09).
    """

    ANALYST = "analyst"            # Análise local do sistema
    CODE = "code"                  # Execução de código
    AGENT = "agent"                # Agente com autonomia
    GITHUB_TOOL = "github_tool"    # Integração com GitHub
    MCP = "mcp"                    # Model Context Protocol
    UTILITY = "utility"            # Utilidade de apoio


class ExtensionLifecycleState(Enum):
    """Estados de ciclo de vida de uma extensão.

    Segue a sequência prevista no CORE_HARDENING_PLAN (hardening 02):

        DISCOVERED → VALIDATED → REGISTERED → INITIALIZING → READY
                                      ↓
                                  RUNNING
                                      ↓
                             DEGRADED / FAILED
                                      ↓
                              STOPPING → STOPPED

    A transição entre estados pertence ao gestor do Runtime (unidades
    posteriores da Fase 8); aqui apenas se declara a taxonomia.
    """

    DISCOVERED = "discovered"
    VALIDATED = "validated"
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass(frozen=True)
class ResourceLimit:
    """Limite declarativo de um recurso consumido por uma extensão.

    Representa uma pretensão de recurso (ex.: cpu, memory_mb, disk_mb)
    com um valor mínimo exigido. A governação efectiva (hardening 05)
    pertence ao Runtime Engine.
    """

    name: str
    value: float

    @property
    def summary(self) -> str:
        """Resumo textual do limite para apresentação."""
        return f"{self.name}={self.value}"


@dataclass(frozen=True)
class ExtensionContract:
    """Contrato mínimo declarativo de uma extensão.

    Define a identidade, a versão do contrato, o tipo, as capacidades
    exigidas, as dependências, os limites de recurso, as permissões e o
    estado de lifecycle de uma extensão. É imutável e validado à
    criação. Contém apenas dados — nenhuma lógica de execução.
    """

    id: str
    name: str
    description: str
    kind: ExtensionKind
    version: str
    contract_version: str
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    resources: tuple[ResourceLimit, ...] = field(default_factory=tuple)
    permissions: tuple[str, ...] = field(default_factory=tuple)
    lifecycle: ExtensionLifecycleState = ExtensionLifecycleState.DISCOVERED
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida o contrato no momento da criação."""
        if not self.id:
            raise ValueError("a extensão precisa de um id não vazio")
        if not self.name:
            raise ValueError("a extensão precisa de um nome (name) não vazio")
        if not self.version:
            raise ValueError("a extensão precisa de uma versão não vazia")
        if not self.contract_version:
            raise ValueError("a extensão precisa de uma versão de contrato não vazia")
        if self.kind is None:
            raise ValueError("a extensão precisa de um tipo (kind) válido")

    @property
    def summary(self) -> str:
        """Resumo textual do contrato para apresentação."""
        return f"{self.name} v{self.version} ({self.kind.value}, lifecycle {self.lifecycle.value})"


__all__ = [
    "ExtensionContract",
    "ExtensionKind",
    "ExtensionLifecycleState",
    "ResourceLimit",
]
