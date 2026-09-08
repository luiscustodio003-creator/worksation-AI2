"""Motor de política de segurança (hardening 09 — Fase 8.8).

Implementa o elo central da cadeia do CORE_HARDENING_PLAN:

    principal -> project -> action -> policy -> decision

com a regra registada na 8.8: **exact-match por acção**. O
``PolicyEngine`` guarda as permissões concedidas por principal (acções
exactas) e responde por cada acção solicitada com uma ``PolicyDecision``
pura e sem efeitos laterais.

O motor **não** sabe o que é uma capacidade, um recurso ou um fornecedor:
recebe strings opacas (principal, projecto, acção) e devolve uma
decisão. A avaliação de capacidade (Fase 4) e de recursos (8.3) continua
fora de âmbito — a política autoriza, não mede nem executa (Artigo 6/2
da Constituição: a API/interface não carrega lógica central — aqui, a
policy também não).
"""

from __future__ import annotations

from wsai2.core.errors import PermissionError, ValidationError

from .base import PolicyDecision, Principal

_ACCAO_PADRAO = "execute"


class PolicyEngine:
    """Avalia se um principal pode executar uma acção dentro de um projecto.

    A instância mantém apenas o catálogo de permissões concedidas
    (imutável por convenção) e é segura para partilhar entre execuções.
    """

    def __init__(self, grants: dict[str, tuple[str, ...]] | None = None) -> None:
        """Cria o motor com o catálogo de acções concedidas por principal.

        Args:
            grants: mapa ``principal_id -> acções concedidas`` (exactas).
                Sem catálogo, nenhum principal tem permissões — acções
                solicitadas são negadas.
        """
        self._grants: dict[str, frozenset[str]] = {
            principal_id: frozenset(acoes)
            for principal_id, acoes in (grants or {}).items()
        }

    def grant(self, principal_id: str, acoes: tuple[str, ...]) -> None:
        """Concede acções exactas a um principal (acumulativo)."""
        existentes = self._grants.get(principal_id, frozenset())
        self._grants[principal_id] = existentes | frozenset(acoes)

    def decide(
        self,
        principal: str,
        project_id: str,
        action: str = _ACCAO_PADRAO,
    ) -> PolicyDecision:
        """Decide se ``principal`` pode executar ``action`` no ``project_id``.

        Args:
            principal: identidade do principal solicitante.
            project_id: projecto sobre o qual a acção incide.
            action: acção solicitada (exact-match com as concedidas).

        Returns:
            A decisão de política (nunca levanta por negação).

        Raises:
            ValidationError: se o principal ou o projecto estiverem vazios.
        """
        if not principal or not principal.strip():
            raise ValidationError(
                "a decisão de política precisa de um principal não vazio",
                code="wsai.security.principal",
            )
        if not project_id or not project_id.strip():
            raise ValidationError(
                "a decisão de política precisa de um project_id não vazio",
                code="wsai.security.project",
            )
        concedidas = self._grants.get(principal, frozenset())
        permitido = action in concedidas
        return PolicyDecision(
            action=action,
            principal=principal,
            project_id=project_id,
            allowed=permitido,
            reason=(
                f"acção '{action}' concedida"
                if permitido
                else f"acção '{action}' não concedida ao principal {principal}"
            ),
        )

    def decide_principal(self, principal: Principal, action: str = _ACCAO_PADRAO) -> PolicyDecision:
        """Decide a partir de um ``Principal`` tipado (portador do projecto)."""
        return self.decide(principal.id, principal.project_id, action)


def denied_decision(decisao: PolicyDecision) -> PermissionError:
    """Converte uma decisão negada no erro taxonómico (8.2).

    Apenas para uso em pontos de enforcement: o erro carrega o motivo da
    decisão como `details`, preservando a observabilidade.
    """
    return PermissionError(
        decisao.reason,
        code="wsai.permission",
        details={
            "action": decisao.action,
            "principal": decisao.principal,
            "project_id": decisao.project_id,
        },
    )


__all__ = ["PolicyEngine", "denied_decision"]