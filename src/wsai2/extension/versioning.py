"""Versioning e compatibilidade de contratos de extensão (hardening 08).

A unidade 8.6 introduz apenas o necessário: leitura semântica da
``contract_version`` que o contrato de extensão (8.1) já declara como
string opaca, e a regra de compatibilidade antes do registo/execução.

Decisão registada nesta unidade (dimensão mínima, hardening 08):

- formato ``major.minor`` (ex.: "1.0"), sem versão de patch;
- **compatível = mesmo ``major``**: dentro do mesmo major presume-se
  retrocompatibilidade; ``minor`` é informativo;
- uma extensão com ``contract_version`` incompatível é **rejeitada
  antes da execução**, nunca corrigida nem executada por aproximação.

A versão do próprio addon (``version``) não é interpretada aqui — o
contrato apenas exige que seja não vazia (já validado na 8.1).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from wsai2.core.errors import ValidationError

# Versão de contrato de extensão suportada pelo núcleo nesta base.
SUPPORTED_CONTRACT_VERSION = "1.0"

_PADRAO = re.compile(r"^\s*(?P<major>\d+)\.(?P<minor>\d+)\s*$")


def _invalida(texto: str) -> ValidationError:
    """Cria o erro de versão de contrato inválida."""
    return ValidationError(
        f"versão de contrato inválida: '{texto}' (esperado major.minor)",
        code="wsai.extension.contract_version",
        details={"versao": texto},
    )


@dataclass(frozen=True)
class ContractVersion:
    """Versão de contrato ``major.minor`` de uma extensão.

    Imutável e construída por ``parse``; não se confunde com a versão do
    addon (que é livre e apenas declarada, não interpretada).
    """

    major: int
    minor: int

    @classmethod
    def parse(cls, texto: str) -> ContractVersion:
        """Interpreta uma versão de contrato ``major.minor``.

        Args:
            texto: representação textual (ex.: "1.0", "2.3").

        Returns:
            A versão de contrato correspondente.

        Raises:
            ValidationError: se o formato não for ``major.minor``.
        """
        if not isinstance(texto, str):
            raise _invalida(texto)
        correspondencia = _PADRAO.match(texto)
        if correspondencia is None:
            raise _invalida(texto)
        return cls(
            major=int(correspondencia.group("major")),
            minor=int(correspondencia.group("minor")),
        )

    def is_compatible_with(self, outra: ContractVersion) -> bool:
        """Indica se esta versão é compatível com ``outra``.

        Compatibilidade = mesmo ``major`` (retrocompatibilidade dentro
        do major); ``minor`` não restringe.
        """
        return self.major == outra.major

    def __str__(self) -> str:
        """Representação textual ``major.minor``."""
        return f"{self.major}.{self.minor}"


__all__ = ["ContractVersion", "SUPPORTED_CONTRACT_VERSION"]