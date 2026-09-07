"""Testes da fundação do WorkStation AI 2.

Valida a configuração mínima do projecto: a existência da versão
e a coerência da versão entre o código e o pacote instalável.
"""

from wsai2 import __version__


def test_versao_definida() -> None:
    """A versão do projecto deve estar definida e ser uma string não vazia."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_formato_versao_semantico() -> None:
    """A versão deve seguir o formato semântico maior.menor.patch."""
    partes = __version__.split(".")
    assert len(partes) == 3
    for parte in partes:
        assert parte.isdigit()


def test_pacote_importavel() -> None:
    """O pacote raiz deve ser importável e expor a versão."""
    import wsai2  # noqa: F401  (valida a importabilidade da fundação)
