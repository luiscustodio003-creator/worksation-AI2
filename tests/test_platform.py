"""Testes do subsistema Platform Foundation.

Valida a detecção de sistema operativo, a construção da descrição neutra
da plataforma e a selecção dos adaptadores pela fábrica.
"""

import os
import sys

import pytest

from wsai2.platform import OperatingSystem, get_platform
from wsai2.platform.base import build_platform_info, detect_operating_system


def test_detectar_sistema_operativo_corrente() -> None:
    """A detecção deve corresponder ao sistema operativo em execução."""
    resultado = detect_operating_system()
    if sys.platform.startswith("win"):
        assert resultado is OperatingSystem.WINDOWS
    elif sys.platform.startswith("linux"):
        assert resultado is OperatingSystem.LINUX
    elif sys.platform.startswith("darwin"):
        assert resultado is OperatingSystem.MACOS


def test_plataforma_detectada_marca_correta() -> None:
    """A descrição construída deve reflectir o sistema operativo indicado."""
    info = build_platform_info(OperatingSystem.WINDOWS)
    assert info.os is OperatingSystem.WINDOWS
    assert info.is_windows is True
    assert info.is_linux is False
    assert info.name


def test_plataforma_linux_marcador_correto() -> None:
    """A descrição Linux deve ter os marcadores adequados."""
    info = build_platform_info(OperatingSystem.LINUX)
    assert info.os is OperatingSystem.LINUX
    assert info.is_linux is True
    assert info.is_windows is False


def test_fabrica_devolve_provider_compatível() -> None:
    """A fábrica deve devolver sempre um provider com o método detect."""
    provider = get_platform()
    info = provider.detect()
    assert isinstance(info.machine, str)
    assert isinstance(info.release, str)
    assert isinstance(info.version, str)


def test_fabrica_devolve_so_corrente() -> None:
    """A fábrica deve devolver um provider coerente com o SO actual."""
    info = get_platform().detect()
    assert info.os is detect_operating_system()