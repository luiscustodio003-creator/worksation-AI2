"""Configuração partilhada do pytest para o WorkStation AI 2.

Disponibiliza fixtures comuns aos testes do projecto.
"""

import os

import pytest


@pytest.fixture
def project_root() -> str:
    """Devolve o caminho absoluto da raiz do projecto."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
