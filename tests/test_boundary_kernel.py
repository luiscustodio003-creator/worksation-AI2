"""Contratos de fronteira do kernel (KERNEL-05/06, consolidadas em KERNEL-07).

Fixa as superfícies públicas de ``execution``, ``resource``, ``security`` e
``runtime_engine``: símbolos sancionados (``__all__``)) e versão de contrato,
e impõe que os consumidores em ``src`` importem apenas ao nível do pacote
(``wsai2.<subsistema>``), nunca módulos internos. As tabelas são importadas
da fonte única de verdade (`architecture_contracts`).
"""

import ast
import pathlib
import re

import wsai2
import wsai2.execution
import wsai2.resource
import wsai2.runtime_engine
import wsai2.security

from .architecture_contracts import (
    GOVERNO_SUPERFICIE,
    OBSERVABILIDADE_SUPERFICIE,
    SUPERFICIES_PUBLICAS,
)

RAIZ_SRC = pathlib.Path(wsai2.__file__).parent

_SUBSISTEMAS_FRONTEIRA = tuple(SUPERFICIES_PUBLICAS)

_MODULOS_FRONTEIRA: dict[str, object] = {
    "execution": wsai2.execution,
    "resource": wsai2.resource,
    "security": wsai2.security,
    "runtime_engine": wsai2.runtime_engine,
}

_VERSIONES: dict[str, str] = {
    "execution": getattr(wsai2.execution, "EXECUTION_CONTRACT_VERSION"),
    "resource": getattr(wsai2.resource, "RESOURCE_CONTRACT_VERSION"),
    "security": getattr(wsai2.security, "SECURITY_CONTRACT_VERSION"),
    "runtime_engine": getattr(wsai2.runtime_engine, "RUNTIME_ENGINE_CONTRACT_VERSION"),
}


def _ficheiros_src() -> list[pathlib.Path]:
    return [
        p
        for p in RAIZ_SRC.rglob("*.py")
        if "__pycache__" not in p.parts
    ]


def test_versao_de_contrato_valida_e_major_minor():
    """A versão de cada fronteira segue a forma ``major.minor``."""
    for subsistema, versao in _VERSIONES.items():
        assert re.fullmatch(r"\d+\.\d+", versao), (
            f"{subsistema}: versão não é major.minor: {versao!r}"
        )


def test_superficies_publicas_congeladas():
    """O ``__all__`` de cada fronteira coincide com a superfície sancionada."""
    for subsistema, superficie in SUPERFICIES_PUBLICAS.items():
        modulo = _MODULOS_FRONTEIRA[subsistema]
        assert set(getattr(modulo, "__all__", [])) == superficie, (
            f"{subsistema}: superfície pública divergente de {sorted(superficie)}"
        )
        nome_constante = f"{subsistema.upper()}_CONTRACT_VERSION"
        assert nome_constante in dir(modulo), (
            f"{subsistema}: falta {nome_constante}"
        )
        assert getattr(modulo, nome_constante) not in superficie, (
            f"{subsistema}: a versão não deve fazer parte da superfície"
        )


def test_subcontrato_de_observabilidade():
    """A fronteira de observabilidade é a fracção sancionada da superfície."""
    superficie = set(getattr(wsai2.runtime_engine, "__all__", []))
    assert OBSERVABILIDADE_SUPERFICIE <= superficie
    assert GOVERNO_SUPERFICIE <= superficie
    assert OBSERVABILIDADE_SUPERFICIE | GOVERNO_SUPERFICIE == superficie
    assert OBSERVABILIDADE_SUPERFICIE.isdisjoint(GOVERNO_SUPERFICIE)


def test_consumidores_apenas_ao_nivel_do_pacote():
    """Consumidores externos importam só ``wsai2.<fronteira>`` (nunca internos)."""
    infraccoes: list[str] = []
    for ficheiro in _ficheiros_src():
        origem = ficheiro.relative_to(RAIZ_SRC).parts[0]
        arvore = ast.parse(ficheiro.read_text(encoding="utf-8"))
        for no in ast.walk(arvore):
            alvos: list[str] = []
            if isinstance(no, ast.ImportFrom) and no.module:
                alvos.append(no.module)
            elif isinstance(no, ast.Import):
                alvos.extend(alias.name for alias in no.names)
            for alvo in alvos:
                partes = alvo.split(".")
                if (
                    len(partes) >= 3
                    and partes[0] == "wsai2"
                    and partes[1] in _SUBSISTEMAS_FRONTEIRA
                    and partes[1] != origem
                ):
                    infraccoes.append(f"{ficheiro.name}: importa internos {alvo}")
    assert infraccoes == [], f"consumo de módulos internos: {infraccoes}"


def test_implementacao_pesada_fora_do_nucleo():
    """KERNEL-09: a mecânica pesada não reside nos pacotes do kernel.

    ``resource`` e ``runtime_engine`` são shells de re-export (apenas
    ``__init__.py``); a implementação pesada vive em
    ``wsai2.infrastructure``, por trás dos contratos públicos.
    """
    for subsistema in ("resource", "runtime_engine"):
        pasta = RAIZ_SRC / subsistema
        internos = [
            p.name
            for p in pasta.iterdir()
            if p.suffix == ".py" and p.name != "__init__.py"
        ]
        assert internos == [], (
            f"{subsistema}: implementação pesada não pode residir no kernel: {internos}"
        )

    obrigatorios = {
        "base_resource.py",
        "base_runtime.py",
        "governor.py",
        "manager.py",
        "monitoring.py",
        "queue.py",
        "scheduler.py",
    }
    infra = RAIZ_SRC / "infrastructure"
    presentes = {p.name for p in infra.iterdir() if p.suffix == ".py"}
    assert obrigatorios <= presentes, (
        f"wsai2.infrastructure: faltam módulos da implementação pesada: "
        f"{sorted(obrigatorios - presentes)}"
    )