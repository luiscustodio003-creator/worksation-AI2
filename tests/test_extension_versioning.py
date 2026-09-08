"""Testes do versioning de contratos de extensão (Fase 8.6).

Valida a leitura semântica da ``contract_version`` (major.minor) e a
regra de compatibilidade registada: **compatível = mesmo major**; a
rejeição ocorre antes do registo/execução (hardening 08).
"""

import pytest

from wsai2.core.errors import ValidationError
from wsai2.extension import ContractVersion, SUPPORTED_CONTRACT_VERSION


def test_versao_parse_validas() -> None:
    """Uma versão major.minor deve ser interpretada correctamente."""
    versao = ContractVersion.parse("1.0")
    assert versao.major == 1
    assert versao.minor == 0
    assert str(versao) == "1.0"


def test_versao_parse_maior_que_nove() -> None:
    """Números com vários dígitos devem ser suportados."""
    versao = ContractVersion.parse("12.34")
    assert versao.major == 12
    assert versao.minor == 34


def test_versao_parse_aceita_espacos_em_volta() -> None:
    """Espaços em branco envolventes não devem invalidar a versão."""
    versao = ContractVersion.parse(" 2.1 ")
    assert versao.major == 2
    assert versao.minor == 1


@pytest.mark.parametrize(
    "invalida",
    ["", "1", "1.", ".5", "1.0.0", "1.0.0-beta", "abc", "1.x", None, 1.0],
)
def test_versao_parse_rejeita_formatos_invalidos(invalida: object) -> None:
    """Formatos fora de major.minor devem ser rejeitados com o código certo."""
    with pytest.raises(ValidationError) as erro:
        ContractVersion.parse(invalida)  # type: ignore[arg-type]
    assert erro.value.code == "wsai.extension.contract_version"


def test_versao_valores_imutaveis() -> None:
    """Uma versão de contrato deve ser imutável (frozen)."""
    versao = ContractVersion.parse("1.0")
    with pytest.raises(Exception):
        versao.major = 2  # type: ignore[misc]


def test_compativel_mesmo_major() -> None:
    """Dentro do mesmo major a compatibilidade deve ser garantida."""
    assert ContractVersion.parse("1.0").is_compatible_with(ContractVersion.parse("1.0"))
    assert ContractVersion.parse("1.9").is_compatible_with(ContractVersion.parse("1.0"))
    assert ContractVersion.parse("2.0").is_compatible_with(ContractVersion.parse("2.5"))


def test_incompativel_major_distinto() -> None:
    """Majors diferentes devem ser sempre incompatíveis."""
    assert not ContractVersion.parse("2.0").is_compatible_with(
        ContractVersion.parse("1.0")
    )
    assert not ContractVersion.parse("1.0").is_compatible_with(
        ContractVersion.parse("0.1")
    )


def test_versao_suportada_constante() -> None:
    """Deve existir uma versão de contrato suportada pela base."""
    assert SUPPORTED_CONTRACT_VERSION == "1.0"
    assert ContractVersion.parse(SUPPORTED_CONTRACT_VERSION).major == 1