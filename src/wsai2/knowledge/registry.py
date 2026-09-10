"""Registo de conhecimento (Fase 9.2).

Segue o padrão dos registos das Fases 4–8 (``CapabilityRegistry``,
``ModelRegistry``, ``ProviderRegistry``, ``ExtensionRegistry``): um
catálogo com consulta por identidade e admissão com id único.

O registo não ingere ficheiros, não extrai, não indexa nem pesquisa:
apenas admite ``KnowledgeRecord`` já válidos, garante a unicidade de
``id`` e responde a consultas. A admissão é o passo de entrada que as
unidades de ingestão posteriores usarão.
"""

from __future__ import annotations

from wsai2.core.public import ValidationError

from .base import KNOWLEDGE_CONTRACT_VERSION, KnowledgeRecord


class KnowledgeRegistry:
    """Registo central de unidades de conhecimento.

    Responsabilidade única: manter o catálogo de ``KnowledgeRecord``
    admitidos e garantir a unicidade de ``id`` na admissão. Não lê
    ficheiros, não executa extracção/indexação e não pesquisa — essas
    responsabilidades pertencem a unidades próprias da Fase 9.
    """

    def __init__(
        self,
        *,
        supported_contract_version: str = KNOWLEDGE_CONTRACT_VERSION,
    ) -> None:
        """Cria um registo ancorado à versão de contrato suportada.

        Args:
            supported_contract_version: versão do contrato de
                conhecimento que o núcleo suporta (ex.: "1.0").
        """
        self._supported = supported_contract_version
        self._records: dict[str, KnowledgeRecord] = {}

    @property
    def supported_contract_version(self) -> str:
        """Versão do contrato de conhecimento suportada pelo registo."""
        return self._supported

    def register(self, record: KnowledgeRecord) -> KnowledgeRecord:
        """Admite um registo único no catálogo.

        Rejeita um ``id`` já presente sem alterar o catálogo.

        Args:
            record: registo de conhecimento já válido (contrato 9.1).

        Returns:
            O registo admitido.

        Raises:
            ValidationError: se o ``id`` já estiver registado.
        """
        if record.id in self._records:
            raise ValidationError(
                f"conhecimento já registado: {record.id}",
                code="wsai.knowledge.duplicate",
                details={"conhecimento": record.id},
            )
        self._records[record.id] = record
        return record

    def unregister(self, record_id: str) -> bool:
        """Remove um registo do catálogo.

        Devolve ``True`` se o registo existia e foi removido.
        """
        return self._records.pop(record_id, None) is not None

    def get(self, record_id: str) -> KnowledgeRecord | None:
        """Obtém um registo pelo id (ou ``None``)."""
        return self._records.get(record_id)

    def has(self, record_id: str) -> bool:
        """Indica se um registo está no catálogo."""
        return record_id in self._records

    def all(self) -> tuple[KnowledgeRecord, ...]:
        """Devolve todos os registos, por ordem de admissão."""
        return tuple(self._records.values())

    def __len__(self) -> int:
        """Número de registos admitidos."""
        return len(self._records)


__all__ = ["KnowledgeRegistry"]