"""Camada de segurança e isolamento de projectos (Fase 8.8).

Subsistema folha da Fase 8 que materializa os hardening 09 (Security /
Policy) e 10 (Project Isolation) do CORE_HARDENING_PLAN, pré-requisitos
do Gate de addons:

- ``base``: tipos puros (``Principal``, ``PolicyDecision``);
- ``policy``: ``PolicyEngine`` de decisão por acção exacta
  (exact-match), sem RBAC nem wildcard;
- ``isolation``: guardas de fronteira de projecto com
  ``ProjectIsolationError``.

Depende apenas de ``wsai2.core`` (erros e contexto) — é uma folha da
árvore de dependências (Artigo 2 da Constituição) e não conhece
extensões, fornecedores nem modelos.
"""

from .base import PolicyDecision, Principal
from .isolation import assert_same_project, require_project
from .policy import PolicyEngine, denied_decision

# Contrato público da fronteira de segurança (KERNEL-05): a superfície
# sancionada é o `__all__` abaixo, congelada por teste de contrato.
SECURITY_CONTRACT_VERSION = "1.0"

__all__ = [
    "PolicyDecision",
    "PolicyEngine",
    "Principal",
    "assert_same_project",
    "denied_decision",
    "require_project",
]