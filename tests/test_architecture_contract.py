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
- ARTIGO 8 — crescimento controlado: subsistemas futuros (api, ui,
  knowledge) não são antecipados como pacotes vazios;
- ARTIGO 13/2 — sem ciclos de import em runtime (arestas tipográficas
  ``TYPE_CHECKING`` não contam).

A lista ``FRONTEIRAS`` espelha exactamente as arestas verificadas na
auditoria da 8.7; qualquer desvio detectado aqui é uma violação de
fronteira a corrigir ou a justificar documentalmente.
"""

from __future__ import annotations

import ast
import pathlib

RAIZ_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "wsai2"
RAIZ_DOCS = pathlib.Path(__file__).resolve().parents[1] / "docs"

# Aresta autorizada: subsistema origem -> subsistema destino.
FRONTEIRAS: frozenset[tuple[str, str]] = frozenset(
    {
        ("capability", "hardware"),
        ("capability", "runtime"),
        ("core", "extension"),
        ("execution", "core"),
        ("execution", "resource"),
        ("extension", "core"),
        ("model", "capability"),
        ("model", "hardware"),
        ("model", "runtime"),
        ("resource", "core"),
        ("resource", "extension"),
        ("resource", "hardware"),
        ("resource", "runtime"),
        ("runtime_engine", "core"),
        ("runtime_engine", "execution"),
        ("runtime_engine", "resource"),
        ("runtime_engine", "task"),
        ("task", "capability"),
        ("task", "hardware"),
        ("task", "model"),
        ("task", "provider"),
        ("task", "runtime"),
    }
)

# Subsistemas funcionais previstos mas ainda não iniciados (Fases 9–11).
SUBSISTEMAS_FUTUROS = ("api", "ui", "knowledge")

# Adaptadores de plataforma: específicos de SO, de acesso reservado.
_ADAPTADORES_SO = ("wsai2.platform.windows", "wsai2.platform.linux")


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
        for adaptador in _ADAPTADORES_SO:
            if adaptador in conteudo:
                infraccoes.append(f"{ficheiro.name}: {adaptador}")
    assert infraccoes == [], f"código de SO referido fora da plataforma: {infraccoes}"


def test_artigo4_factory_e_o_ponto_unico_de_entrada_da_plataforma() -> None:
    """A API pública da plataforma não expõe os adaptadores directamente."""
    init_platform = (RAIZ_SRC / "platform" / "__init__.py").read_text(encoding="utf-8")
    for adaptador in _ADAPTADORES_SO:
        assert adaptador not in init_platform
    assert "get_platform" in init_platform


def test_artigo4_adaptadores_nao_se_importam_entre_si() -> None:
    """Windows e Linux devem depender apenas da base comum (base.py)."""
    for nome in ("windows.py", "linux.py"):
        conteudo = (RAIZ_SRC / "platform" / nome).read_text(encoding="utf-8")
        for outro in _ADAPTADORES_SO:
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


def test_artigo8_subsistemas_futuros_nao_antecipados() -> None:
    """API, UI e Knowledge não podem existir como pastas placeholder."""
    antecipados: list[str] = []
    for nome in SUBSISTEMAS_FUTUROS:
        if (RAIZ_SRC / nome).exists():
            antecipados.append(nome)
    assert antecipados == [], f"subsistemas antecipados sem necessidade: {antecipados}"


def test_artigo8_nenhuma_pasta_placeholder() -> None:
    """Nenhum subsistema existe apenas com ``__init__.py`` sem re-exportações."""
    for subsistema in _subsistemas_src():
        pasta = RAIZ_SRC / subsistema
        ficheiros = [
            p
            for p in pasta.iterdir()
            if p.suffix == ".py" and p.name != "__init__.py"
        ]
        assert ficheiros, f"{subsistema} é uma pasta placeholder (só __init__.py)"
        init = pasta / "__init__.py"
        if init.exists():
            arvore = ast.parse(init.read_text(encoding="utf-8"))
            re_exporta = any(
                isinstance(no, ast.ImportFrom)
                for no in ast.walk(arvore)
            )
            assert re_exporta, f"{subsistema}/__init__.py não re-exporta nada"