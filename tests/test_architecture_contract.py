"""Testes de contrato arquitectural (Fase 8.7 — hardening 11).

Transformam regras da CONSTITUTION/AGENTS em testes executáveis sobre o
repositório real:

- ARTIGO 1/10 — responsabilidade e documentação: todo o ficheiro de
  ``src/wsai2`` possui docstring de módulo e cada subsistema tem base
  documental em ``docs/<subsistema>/BASE-*.md``;
- ARTIGO 2/13 — dependências para dentro: o grafo de import entre
  subsistemas pertence a uma lista explícita (``FRONTEIRAS``);
- ARTIGO 4 — código específico de SO isolado na camada de plataforma,
  alcançável apenas através da fábrica;
- ARTIGO 8 — crescimento controlado: subsistemas ainda não iniciados
  (api, ui) não são antecipados como pacotes vazios. O subsistema
  ``knowledge`` passou a estar autorizado na unidade 9.1 (Fase 9
  aprovada no estado persistente) — deixa de constar desta lista;
- ARTIGO 13/2 — sem ciclos de import em runtime (arestas tipográficas
  ``TYPE_CHECKING`` não contam).

A lista ``FRONTEIRAS`` espelha exactamente as arestas verificadas na
auditoria da 8.7; qualquer desvio detectado aqui é uma violação de
fronteira a corrigir ou a justificar documentalmente.
"""

from __future__ import annotations

import ast
import importlib
import pathlib
import re

from .architecture_contracts import (
    ADAPTADORES_SO,
    CONTRACT_VERSIONES,
    CONTRATO_CONSTANTES,
    FIREWALL,
    FRONTEIRAS,
    KERNEL_SUBSISTEMAS,
    MODULO_CONTRATO,
    SUBSISTEMAS_FUTUROS,
)

RAIZ_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "wsai2"
RAIZ_DOCS = pathlib.Path(__file__).resolve().parents[1] / "docs"

def _ficheiros_src() -> list[pathlib.Path]:
    """Todos os ficheiros Python de ``src/wsai2`` (exclui __pycache__)."""
    return [
        p
        for p in RAIZ_SRC.rglob("*.py")
        if "__pycache__" not in p.parts
    ]


def _subsistemas_src() -> list[str]:
    """Nomes dos subsistemas (directórios) com código."""
    return sorted(
        p.name for p in RAIZ_SRC.iterdir()
        if p.is_dir() and not p.name.startswith("__")
    )


def _em_bloco_type_checking(no: ast.AST) -> bool:
    """Indica se o nó de import está dentro de ``if TYPE_CHECKING:``."""
    bloco_atual: ast.AST | None = no
    while bloco_atual is not None:
        if isinstance(bloco_atual, ast.If):
            condicao = bloco_atual.test
            if isinstance(condicao, ast.Name) and condicao.id == "TYPE_CHECKING":
                return True
        bloco_atual = getattr(bloco_atual, "_parent", None)
    return False


def _arestas_import(ficheiro: pathlib.Path, *, excluir_tipagem: bool) -> set[tuple[str, str]]:
    """Arestas de import (subsistema -> subsistema) declaradas num ficheiro.

    As importações ``wsai2.<x>`` são normalizadas para o nome de topo
    (ex.: ``wsai2.hardware`` -> ``hardware``). Importações relativas
    (``.base``, ``..``) nunca saem do próprio subsistema e são ignoradas.
    Quando ``excluir_tipagem``, os imports dentro de ``if TYPE_CHECKING:``
    (tipográficos, sem dependência em runtime) são omitidos.
    """
    arvore = ast.parse(ficheiro.read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        for filho in ast.iter_child_nodes(no):
            setattr(filho, "_parent", no)
    origem = ficheiro.relative_to(RAIZ_SRC).parts[0]
    arestas: set[tuple[str, str]] = set()
    for no in ast.walk(arvore):
        if excluir_tipagem and _em_bloco_type_checking(no):
            continue
        destino: str | None = None
        if isinstance(no, ast.ImportFrom) and no.module:
            partes = no.module.split(".")
            if partes[0] == "wsai2" and len(partes) >= 2:
                destino = partes[1]
        elif isinstance(no, ast.Import):
            for alias in no.names:
                partes = alias.name.split(".")
                if partes[0] == "wsai2" and len(partes) >= 2:
                    destino = partes[1]
        if destino is not None and destino != origem:
            arestas.add((origem, destino))
    return arestas


def test_artigo1_10_todos_os_fontes_tem_docstring_de_modulo() -> None:
    """Cada módulo de ``src/wsai2`` deve documentar a sua finalidade."""
    sem_docstring: list[str] = []
    for ficheiro in _ficheiros_src():
        arvore = ast.parse(ficheiro.read_text(encoding="utf-8"))
        doc = ast.get_docstring(arvore, clean=False)
        if not doc or not doc.strip():
            sem_docstring.append(str(ficheiro.relative_to(RAIZ_SRC.parents[0])))
    assert sem_docstring == [], f"módulos sem docstring: {sem_docstring}"


def test_artigo10_todos_os_subsistemas_tem_base_documental() -> None:
    """Cada subsistema implementado deve ter documentação própria."""
    sem_base: list[str] = []
    for subsistema in _subsistemas_src():
        base_docs = list((RAIZ_DOCS / subsistema).glob("BASE-*.md"))
        if not base_docs:
            sem_base.append(subsistema)
    assert sem_base == [], f"subsistemas sem docs/<nome>/BASE-*.md: {sem_base}"


def test_artigo2_13_arestas_respeitam_fronteiras() -> None:
    """Nenhum import pode atravessar subsistemas fora da lista autorizada."""
    violacoes: list[tuple[str, str, str]] = []
    for ficheiro in _ficheiros_src():
        for origem, destino in _arestas_import(ficheiro, excluir_tipagem=False):
            if (origem, destino) not in FRONTEIRAS:
                violacoes.append((origem, destino, ficheiro.name))
    assert violacoes == [], f"fronteiras violadas (origem->destino, ficheiro): {violacoes}"


def test_artigo2_13_firewall_por_subsistema() -> None:
    """Cada subsistema só depende dos destinos autorizados (firewall exacto).

    Mais estrito que o `FRONTEIRAS` (união): detecta automaticamente
    qualquer aresta nova, mesmo dentro da união. A chave do firewall deve
    cobrir todos os subsistemas do código.
    """
    grafo: dict[str, set[str]] = {s: set() for s in _subsistemas_src()}
    for ficheiro in _ficheiros_src():
        for origem, destino in _arestas_import(ficheiro, excluir_tipagem=False):
            grafo[origem].add(destino)

    assert set(FIREWALL) == set(_subsistemas_src())
    for origem, destinos in grafo.items():
        permitidos = FIREWALL.get(origem, frozenset())
        ilegais = destinos - permitidos
        assert ilegais == set(), f"firewall violado por {origem}: {sorted(ilegais)}"


def test_kernel_todas_as_superficies_publicas_versionadas() -> None:
    """Todos os subsistemas do kernel expõem superfície versionada (KERNEL-07).

    O bump de versão (ex.: 1.0 -> 1.1) é uma alteração deliberada: exige
    actualizar simultaneamente o código e esta tabela esperada.
    """
    for subsistema in KERNEL_SUBSISTEMAS:
        modulo = importlib.import_module(MODULO_CONTRATO[subsistema])
        nome_constante = CONTRATO_CONSTANTES[subsistema]
        versao = getattr(modulo, nome_constante)
        assert re.fullmatch(r"\d+\.\d+", versao), (
            f"{subsistema}: versão não é major.minor: {versao!r}"
        )
        assert versao == CONTRACT_VERSIONES[subsistema], (
            f"{subsistema}: versão {versao!r} != esperada "
            f"{CONTRACT_VERSIONES[subsistema]!r}"
        )
        if subsistema != "core":
            assert nome_constante not in set(getattr(modulo, "__all__", [])), (
                f"{subsistema}: a versão não deve fazer parte da superfície"
            )


def test_artigo2_imports_apontam_para_subsistemas_reais() -> None:
    """O destino de cada import deve ser um subsistema existente."""
    conhecidos = set(_subsistemas_src())
    desconhecidos: list[tuple[str, str, str]] = []
    for ficheiro in _ficheiros_src():
        for origem, destino in _arestas_import(ficheiro, excluir_tipagem=False):
            if destino not in conhecidos:
                desconhecidos.append((origem, destino, ficheiro.name))
    assert desconhecidos == [], f"imports para subsistemas inexistentes: {desconhecidos}"


def test_artigo4_adaptadores_os_acessiveis_so_na_plataforma() -> None:
    """Nenhum ficheiro fora de ``platform`` pode importar adaptadores de SO."""
    infraccoes: list[str] = []
    for ficheiro in _ficheiros_src():
        if ficheiro.parent.name == "platform":
            continue
        conteudo = ficheiro.read_text(encoding="utf-8")
        for adaptador in ADAPTADORES_SO:
            if adaptador in conteudo:
                infraccoes.append(f"{ficheiro.name}: {adaptador}")
    assert infraccoes == [], f"código de SO referido fora da plataforma: {infraccoes}"


def test_artigo4_factory_e_o_ponto_unico_de_entrada_da_plataforma() -> None:
    """A API pública da plataforma não expõe os adaptadores directamente."""
    init_platform = (RAIZ_SRC / "platform" / "__init__.py").read_text(encoding="utf-8")
    for adaptador in ADAPTADORES_SO:
        assert adaptador not in init_platform
    assert "get_platform" in init_platform


def test_artigo4_adaptadores_nao_se_importam_entre_si() -> None:
    """Windows e Linux devem depender apenas da base comum (base.py)."""
    for nome in ("windows.py", "linux.py"):
        conteudo = (RAIZ_SRC / "platform" / nome).read_text(encoding="utf-8")
        for outro in ADAPTADORES_SO:
            assert outro not in conteudo, f"{nome} depende de {outro}"


def test_artigo2_13_sem_ciclos_de_import_em_runtime() -> None:
    """O grafo de import em runtime (sem TYPE_CHECKING) deve ser acíclico."""
    grafo: dict[str, set[str]] = {s: set() for s in _subsistemas_src()}
    for ficheiro in _ficheiros_src():
        for origem, destino in _arestas_import(ficheiro, excluir_tipagem=True):
            grafo[origem].add(destino)

    visitado: set[str] = set()
    em_stack: set[str] = set()
    ciclos: list[tuple[str, str]] = []

    def dfs(no: str) -> None:
        visitado.add(no)
        em_stack.add(no)
        for vizinho in grafo.get(no, ()):
            if vizinho not in visitado:
                dfs(vizinho)
            elif vizinho in em_stack:
                ciclos.append((no, vizinho))
        em_stack.discard(no)

    for subsistema in grafo:
        if subsistema not in visitado:
            dfs(subsistema)
    assert ciclos == [], f"ciclos de import em runtime: {ciclos}"


def test_consumidores_core_apenas_via_public() -> None:
    """KERNEL-08: o `core` é importado pelos consumidores só via `wsai2.core.public`.

    Fora do pacote ``core`` não podem existir imports absolutos directos a
    ``wsai2.core.errors`` ou ``wsai2.core.context`` — a taxonomia e o
    contexto são alcançáveis exclusivamente através da superfície
    versionada ``wsai2.core.public``.
    """
    proibidos = ("wsai2.core.errors", "wsai2.core.context")
    fora_da_regra: list[str] = []
    for ficheiro in _ficheiros_src():
        if ficheiro.relative_to(RAIZ_SRC).parts[0] == "core":
            continue
        arvore = ast.parse(ficheiro.read_text(encoding="utf-8"))
        infractores: list[str] = []
        for no in ast.walk(arvore):
            if isinstance(no, ast.ImportFrom) and no.module and no.module.startswith(proibidos):
                infractores.append(
                    f"{no.lineno}: from {no.module} import "
                    f"{', '.join(a.name for a in no.names)}"
                )
            elif isinstance(no, ast.Import):
                for alias in no.names:
                    if alias.name.startswith(proibidos):
                        infractores.append(f"{no.lineno}: import {alias.name}")
        if infractores:
            fora_da_regra.append(f"{ficheiro.relative_to(RAIZ_SRC.parents[0])}: {infractores}")
    assert fora_da_regra == [], (
        "consumidores do core devem importar apenas de 'wsai2.core.public': "
        f"{fora_da_regra}"
    )


def test_artigo8_subsistemas_futuros_nao_antecipados() -> None:
    """API e UI não podem existir como pastas placeholder antes das Fases 10–11."""
    antecipados: list[str] = []
    for nome in SUBSISTEMAS_FUTUROS:
        if (RAIZ_SRC / nome).exists():
            antecipados.append(nome)
    assert antecipados == [], f"subsistemas antecipados sem necessidade: {antecipados}"


def test_artigo8_nenhuma_pasta_placeholder() -> None:
    """Nenhum subsistema existe apenas com ``__init__.py`` sem re-exportações.

    Excepção KERNEL-09: ``resource`` e ``runtime_engine`` são shells de
    re-export deliberados — a sua implementação pesada desceu para
    ``wsai2.infrastructure``; continuam a existir como fronteira (__init__
    com re-exportações + versão), não como pasta vazia.
    """
    shells_de_reesportacao = {"resource", "runtime_engine"}
    for subsistema in _subsistemas_src():
        pasta = RAIZ_SRC / subsistema
        ficheiros = [
            p
            for p in pasta.iterdir()
            if p.suffix == ".py" and p.name != "__init__.py"
        ]
        assert ficheiros or subsistema in shells_de_reesportacao, (
            f"{subsistema} é uma pasta placeholder (só __init__.py)"
        )
        init = pasta / "__init__.py"
        if init.exists():
            arvore = ast.parse(init.read_text(encoding="utf-8"))
            re_exporta = any(
                isinstance(no, ast.ImportFrom)
                for no in ast.walk(arvore)
            )
            assert re_exporta, f"{subsistema}/__init__.py não re-exporta nada"