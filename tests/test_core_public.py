"""Testes da superfície pública do núcleo (KERNEL-03).

Valida que `wsai2.core.public` expõe o contrato versionado dos 14 símbolos
estáveis do `core` folha, mantém identidade com `wsai2.core` (sem drift nem
lógica própria) e não alcança outros subsistemas (firewall preservado).
"""

import ast

import pathlib

import wsai2.core as core
import wsai2.core.public as public

SUPERFICIE = frozenset(
    {
        "CORE_PUBLIC_CONTRACT_VERSION",
        "CancellationToken",
        "CapabilityError",
        "CancellationError",
        "ExecutionContext",
        "ExecutionError",
        "ExecutionPriority",
        "ModelError",
        "PermissionError",
        "ProjectIsolationError",
        "ProviderError",
        "ResourceError",
        "TimeoutError",
        "ValidationError",
        "WsaiError",
    }
)

CONTRATO = SUPERFICIE - {"CORE_PUBLIC_CONTRACT_VERSION"}


def test_versao_do_contrato():
    """A versão do contrato existe, é "major.minor" e é numérica."""
    assert hasattr(public, "CORE_PUBLIC_CONTRACT_VERSION")
    versao = public.CORE_PUBLIC_CONTRACT_VERSION
    partes = versao.split(".")
    assert len(partes) == 2
    assert all(parte.isdigit() for parte in partes)


def test_superficie_completa_e_declarada():
    """Todos os símbolos do contrato existem e `__all__` é exacto."""
    for nome in SUPERFICIE:
        assert hasattr(public, nome)
    assert frozenset(public.__all__) == SUPERFICIE


def test_identidade_com_o_core():
    """Os símbolos re-exportados são os mesmos objectos de `wsai2.core`."""
    for nome in CONTRATO:
        assert getattr(public, nome) is getattr(core, nome)


def test_public_nao_depende_de_outros_subsistemas():
    """A fachada só importa do próprio leaf `core` (firewall intacto)."""
    ficheiro = pathlib.Path(public.__file__)
    arvore = ast.parse(ficheiro.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            assert no.module == "wsai2.core" or no.module.startswith("wsai2.core."), (
                f"import ilegal em core/public.py: {no.module}"
            )


def test_public_sem_logica_propria():
    """A fachada não define classes nem funções novas (só re-exporta)."""
    ficheiro = pathlib.Path(public.__file__)
    arvore = ast.parse(ficheiro.read_text(encoding="utf-8"))
    definicoes = [
        no
        for no in ast.walk(arvore)
        if isinstance(no, (ast.FunctionDef, ast.ClassDef))
    ]
    assert definicoes == []