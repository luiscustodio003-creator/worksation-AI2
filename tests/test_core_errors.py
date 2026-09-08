"""Testes da taxonomia transversal de erros (Fase 8.2).

Valida a hierarquia do modelo de erros unificado: herança comum,
códigos estáveis por categoria e transporte de detalhes opacos.
"""

import pytest

from wsai2.core import (
    CancellationError,
    CapabilityError,
    ExecutionError,
    ModelError,
    PermissionError,
    ProjectIsolationError,
    ProviderError,
    ResourceError,
    TimeoutError,
    ValidationError,
    WsaiError,
)

_CATEGORIAS = (
    ValidationError,
    CapabilityError,
    ModelError,
    ProviderError,
    ResourceError,
    TimeoutError,
    CancellationError,
    PermissionError,
    ProjectIsolationError,
    ExecutionError,
)


def test_todas_as_categorias_herdam_de_wsai_error() -> None:
    """Cada categoria da taxonomia deve descender do erro base."""
    for categoria in _CATEGORIAS:
        assert issubclass(categoria, WsaiError), categoria


def test_erro_base_transporta_code_e_details() -> None:
    """Um erro base deve preservar mensagem, código e detalhes."""
    erro = WsaiError("falhou", code="wsai.teste", details={"origem": "teste"})
    assert erro.message == "falhou"
    assert erro.code == "wsai.teste"
    assert erro.details == {"origem": "teste"}


def test_code_predefinido_por_categoria() -> None:
    """Cada categoria deve expor o código estável da sua rubrica."""
    esperados: dict[type[WsaiError], str] = {
        ValidationError: "wsai.validation",
        CapabilityError: "wsai.capability",
        ModelError: "wsai.model",
        ProviderError: "wsai.provider",
        ResourceError: "wsai.resource",
        TimeoutError: "wsai.timeout",
        CancellationError: "wsai.cancellation",
        PermissionError: "wsai.permission",
        ProjectIsolationError: "wsai.project_isolation",
        ExecutionError: "wsai.execution",
    }
    for categoria, code in esperados.items():
        assert categoria("msg").code == code


def test_detalhes_opcionais_por_omissao_vazios() -> None:
    """Sem detalhes fornecidos, o mapa deve estar vazio."""
    erro = ValidationError("dados inválidos")
    assert erro.details == {}


def test_mensagem_preservada_no_str() -> None:
    """A mensagem original deve ser a representação do erro."""
    assert str(CapabilityError("sem capacidade")) == "sem capacidade"


def test_categorias_prontas_para_uso_como_pytest_raises() -> None:
    """As categorias devem poder ser capturadas com pytest.raises."""
    with pytest.raises(ProviderError):
        raise ProviderError("fornecedor indisponível")


def test_provider_error_serve_de_base_para_alinhamento_futuro() -> None:
    """ProviderError é a base prevista para o alinhamento do AdapterError."""
    assert issubclass(ProviderError, WsaiError)
    assert issubclass(ProviderError, Exception)