"""Registo de extensões (Fase 8.6).

Segue o padrão dos registos das Fases 4–6 (``CapabilityRegistry``,
``ModelRegistry``, ``ProviderRegistry``): um catálogo com consulta por
identidade. Mantém o **estado de lifecycle no próprio contrato** (o
``RuntimeStatus`` não é uma entidade nova — é o ``lifecycle`` do
``ExtensionContract``), evitando estado duplicado fora do registo.

O registo não executa addons nem lança trabalho: apenas regista,
valida versões de contrato (hardening 08) e responde a consultas. As
transições de estado são delegadas na máquina de lifecycle (``lifecycle``).

Na Fase 8.9 (Gate de addons), o registo materializa a ponte entre o
vocabulário declarativo ``permissions`` do contrato (hardening 01) e a
política de segurança (hardening 09): quando um motor de política é
fornecido à entrada, cada permissão declarada é concedida **como acção
exacta** ao principal identificado pelo ``id`` da extensão. Sem motor, o
registo comporta-se exactamente como antes.
"""

from __future__ import annotations

from wsai2.core.public import ValidationError
from wsai2.security import PolicyEngine

from .base import ExtensionContract, ExtensionLifecycleState
from .lifecycle import transition
from .versioning import SUPPORTED_CONTRACT_VERSION, ContractVersion


class ExtensionRegistry:
    """Registo central de extensões conhecidas.

    Responsabilidade única: manter o catálogo de extensões registadas
    (com o seu estado de lifecycle) e validar a compatibilidade de
    contrato no registo. Não detecta, não executa e não gere recursos —
    essas responsabilidades pertencem a unidades próprias da Fase 8.
    """

    def __init__(
        self,
        *,
        supported_contract_version: str = SUPPORTED_CONTRACT_VERSION,
    ) -> None:
        """Cria um registo ancorado a uma versão de contrato suportada.

        Args:
            supported_contract_version: versão do contrato de extensão
                que o núcleo suporta (ex.: "1.0").
        """
        self._supported = ContractVersion.parse(supported_contract_version)
        self._extensions: dict[str, ExtensionContract] = {}

    @property
    def supported_contract_version(self) -> str:
        """Versão do contrato de extensão suportada pelo registo."""
        return str(self._supported)

    def register(
        self,
        contrato: ExtensionContract,
        *,
        policy: PolicyEngine | None = None,
    ) -> ExtensionContract:
        """Regista uma extensão já validada, movendo-a para ``REGISTERED``.

        Valida a unicidade da identidade, a compatibilidade da
        ``contract_version`` com o núcleo (hardening 08) e o estado
        (deve estar ``VALIDATED``, seguindo o fluxo do hardening 02).

        Quando ``policy`` é fornecida (Gate de addons, 8.9), o registo
        concede as ``permissions`` declaradas como **acções exactas** ao
        principal com o ``id`` da extensão — a ponte entre o vocabulário
        declarativo do contrato e o ``PolicyEngine`` da 8.8. Apenas
        procede após o registo ser aceite; uma negação de política não
        impede o registo (o catálogo e a política são entidades
        distintas).

        Args:
            contrato: extensão no estado ``VALIDATED``.
            policy: motor de política opcional que recebe os grants
                derivados das permissões declaradas.

        Returns:
            O contrato registado, no estado ``REGISTERED``.

        Raises:
            ValidationError: identidade duplicada, estado errado,
                ``contract_version`` inválida ou incompatível.
        """
        if contrato.id in self._extensions:
            raise ValidationError(
                f"extensão já registada: {contrato.id}",
                code="wsai.extension.duplicate",
                details={"extensao": contrato.id},
            )
        versao_contrato = ContractVersion.parse(contrato.contract_version)
        if not versao_contrato.is_compatible_with(self._supported):
            raise ValidationError(
                f"extensão '{contrato.id}' usa contrato {versao_contrato}; "
                f"o núcleo suporta {self._supported}",
                code="wsai.extension.contract_incompatible",
                details={
                    "extensao": contrato.id,
                    "requerido": str(versao_contrato),
                    "suportado": str(self._supported),
                },
            )
        if contrato.lifecycle is not ExtensionLifecycleState.VALIDATED:
            raise ValidationError(
                f"registar exige uma extensão VALIDATED: {contrato.id}",
                code="wsai.extension.lifecycle",
                details={"extensao": contrato.id, "estado": contrato.lifecycle.value},
            )
        registado = transition(contrato, ExtensionLifecycleState.REGISTERED)
        self._extensions[contrato.id] = registado
        if policy is not None and contrato.permissions:
            policy.grant(contrato.id, contrato.permissions)
        return registado

    def unregister(self, extension_id: str) -> bool:
        """Remove uma extensão do catálogo.

        Devolve ``True`` se a extensão existia e foi removida.
        """
        return self._extensions.pop(extension_id, None) is not None

    def get(self, extension_id: str) -> ExtensionContract | None:
        """Obtém o contrato de uma extensão pelo id (ou ``None``)."""
        return self._extensions.get(extension_id)

    def has(self, extension_id: str) -> bool:
        """Indica se uma extensão está registada."""
        return extension_id in self._extensions

    def all(self) -> tuple[ExtensionContract, ...]:
        """Devolve todos os contratos registados, por ordem de registo."""
        return tuple(self._extensions.values())

    def __len__(self) -> int:
        """Número de extensões registadas."""
        return len(self._extensions)

    def state(self, extension_id: str) -> ExtensionLifecycleState:
        """Estado de lifecycle actual de uma extensão.

        Raises:
            ValidationError: se a extensão não estiver registada.
        """
        contrato = self._extensions.get(extension_id)
        if contrato is None:
            raise ValidationError(
                f"extensão desconhecida: {extension_id}",
                code="wsai.extension.unknown",
                details={"extensao": extension_id},
            )
        return contrato.lifecycle

    def transition_state(
        self,
        extension_id: str,
        destino: ExtensionLifecycleState,
    ) -> ExtensionContract:
        """Move uma extensão registada para ``destino`` (transição validada).

        Persiste o novo estado no catálogo e devolve o contrato novo.

        Raises:
            ValidationError: se a extensão for desconhecida ou a
                transição não for permitida.
        """
        contrato = self._extensions.get(extension_id)
        if contrato is None:
            raise ValidationError(
                f"extensão desconhecida: {extension_id}",
                code="wsai.extension.unknown",
                details={"extensao": extension_id},
            )
        novo = transition(contrato, destino)
        self._extensions[extension_id] = novo
        return novo


__all__ = ["ExtensionRegistry"]