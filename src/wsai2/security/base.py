"""Tipos fundamentais da camada de segurança (Fase 8.8).

É nesta unidade (hardening 09 do CORE_HARDENING_PLAN) que a taxonomia de
erros fechada na 8.2 (`PermissionError`, `ProjectIsolationError`) ganha
emissores e contrato. Este módulo contém apenas tipos puros e imutáveis:
o **principal** que executa (utilizador/agente), o âmbito de projecto a
que se refere e a **decisão** de política.

Regra registada nesta unidade: a política é **exact-match por acção** —
uma acção é concedida se e só se estiver declarada nas permissões
(granted) do principal. Não há RBAC, hierarquias nem wildcard (escopo
mínimo para o Gate de addons, Artigo 8 da Constituição). A cadeia
``principal -> project -> action -> policy -> decision`` é implementada
em ``policy.py`` e ``isolation.py``; este módulo apenas a tipa.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Principal:
    """Sujeito que solicita uma acção (utilizador, agente ou extensão).

    Carrega a identidade e, quando pertinente, o projecto sobre o qual
    pretende agir. Não contém segredos nem credenciais — é apenas o
    portador da intenção declarada.
    """

    id: str
    project_id: str = ""
    permissions: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_project(self) -> bool:
        """Indica se o principal está vinculado a um projecto."""
        return bool(self.project_id)

    @property
    def summary(self) -> str:
        """Resumo textual do principal para apresentação."""
        projecto = f" (projecto {self.project_id})" if self.has_project else ""
        return f"{self.id}{projecto}"


@dataclass(frozen=True)
class PolicyDecision:
    """Resultado de uma decisão de política sobre uma acção.

    Transporta a acção, o principal e o projecto avaliados, o veredicto
    e a justificação em linguagem natural — para observabilidade no
    ``ExecutionReport`` sem dependências do mapa de permissões.
    """

    action: str
    principal: str
    project_id: str
    allowed: bool
    reason: str


__all__ = ["PolicyDecision", "Principal"]