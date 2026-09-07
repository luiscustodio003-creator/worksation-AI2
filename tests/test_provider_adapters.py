"""Testes dos adaptadores de runtime do Provider Layer.

Valida a interface de comunicação com os runtimes (listar modelos e
gerar texto) usando transports injectáveis determinísticos, e o
transporte HTTP real contra um servidor local.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from wsai2.provider import (
    AdapterError,
    OllamaAdapter,
    OpenAiCompatibleAdapter,
    ProviderDefinition,
    ProviderType,
    RuntimeAdapter,
    adapter_factory_names,
    build_adapter,
    create_default_registry,
    default_providers,
)
from wsai2.provider.adapters import Transport, TransportResult
from wsai2.provider.transports import http_json_transport


class _TransporteRecorder:
    """Transport injectável que regista as chamadas feitas."""

    def __init__(self, resposta: TransportResult) -> None:
        self.resposta = resposta
        self.chamadas: list[tuple[str, str, object | None]] = []

    def __call__(self, url: str, method: str, payload: object | None) -> TransportResult:
        self.chamadas.append((url, method, payload))
        return self.resposta


def _definicao(provider_id: str) -> ProviderDefinition:
    return next(
        provider
        for provider in default_providers()
        if provider.id == provider_id
    )


# --------------------------------------------------------------- Ollama
def test_ollama_lista_modelos() -> None:
    """Ollama deve listar modelos de /api/tags."""
    corpo = json.dumps({"models": [{"name": "qwen2.5:7b"}, {"name": "phi3:mini"}]})
    transporte = _TransporteRecorder((200, corpo))
    adaptador = OllamaAdapter(transporte)

    modelos = adaptador.list_models("http://localhost:11434")

    assert modelos == ("qwen2.5:7b", "phi3:mini")
    assert transporte.chamadas == [
        ("http://localhost:11434/api/tags", "GET", None)
    ]


def test_ollama_gera_texto() -> None:
    """Ollama deve gerar texto via /api/generate com stream desactivado."""
    corpo = json.dumps({"response": "Olá do Ollama."})
    transporte = _TransporteRecorder((200, corpo))
    adaptador = OllamaAdapter(transporte)

    texto = adaptador.generate(
        "http://localhost:11434",
        "qwen2.5:7b",
        "Olá",
        max_tokens=128,
    )

    assert texto == "Olá do Ollama."
    url, method, payload = transporte.chamadas[0]
    assert url == "http://localhost:11434/api/generate"
    assert method == "POST"
    assert payload == {
        "model": "qwen2.5:7b",
        "prompt": "Olá",
        "stream": False,
        "options": {"num_predict": 128},
    }


def test_ollama_resposta_sem_modelos() -> None:
    """A ausência do campo 'models' deve falhar com AdapterError."""
    transporte = _TransporteRecorder((200, json.dumps({})))
    adaptador = OllamaAdapter(transporte)

    try:
        adaptador.list_models("http://localhost:11434")
        assert False, "deveria lançar AdapterError"
    except AdapterError as exc:
        assert "models" in str(exc)


# ---------------------------------------------- API compatível com OpenAI
def test_openai_compativel_lista_modelos() -> None:
    """O adaptador compatível deve listar modelos de /v1/models."""
    corpo = json.dumps({"data": [{"id": "llama3"}, {"id": "gpt-4o"}]})
    transporte = _TransporteRecorder((200, corpo))
    adaptador = OpenAiCompatibleAdapter(transporte)

    modelos = adaptador.list_models("http://localhost:8080")

    assert modelos == ("llama3", "gpt-4o")
    assert transporte.chamadas == [("http://localhost:8080/v1/models", "GET", None)]


def test_openai_compativel_gera_texto() -> None:
    """O adaptador compatível deve gerar texto via chat/completions."""
    corpo = json.dumps({"choices": [{"message": {"content": "Resposta."}}]})
    transporte = _TransporteRecorder((200, corpo))
    adaptador = OpenAiCompatibleAdapter(transporte)

    texto = adaptador.generate("http://localhost:8080", "llama3", "Olá")

    assert texto == "Resposta."
    url, method, payload = transporte.chamadas[0]
    assert url == "http://localhost:8080/v1/chat/completions"
    assert method == "POST"
    assert payload == {
        "model": "llama3",
        "messages": [{"role": "user", "content": "Olá"}],
        "max_tokens": 256,
    }


def test_adaptador_compativel_sem_conteudo() -> None:
    """Choices vazios ou sem content devem falhar com AdapterError."""
    transporte = _TransporteRecorder((200, json.dumps({"choices": []})))
    adaptador = OpenAiCompatibleAdapter(transporte)

    try:
        adaptador.generate("http://localhost:8080", "llama3", "Olá")
        assert False, "deveria lançar AdapterError"
    except AdapterError as exc:
        assert "conteúdo" in str(exc)


# ------------------------------------------------------------------- erros
def test_estado_http_de_erro_falha() -> None:
    """Um estado HTTP >= 400 deve falhar com AdapterError."""
    transporte = _TransporteRecorder((404, "not found"))
    adaptador = OllamaAdapter(transporte)

    try:
        adaptador.list_models("http://localhost:11434")
        assert False, "deveria lançar AdapterError"
    except AdapterError as exc:
        assert "404" in str(exc)


def test_json_invalido_falha() -> None:
    """Uma resposta não JSON deve falhar com AdapterError."""
    transporte = _TransporteRecorder((200, "isto não é JSON"))
    adaptador = OllamaAdapter(transporte)

    try:
        adaptador.generate("http://localhost:11434", "m", "p")
        assert False, "deveria lançar AdapterError"
    except AdapterError as exc:
        assert "JSON" in str(exc)


# ------------------------------------------------------------------- fábrica
def test_adaptadores_registados_no_catalogo() -> None:
    """Devem existir adaptadores para os fornecedores do catálogo base."""
    nomes = adapter_factory_names()
    ids_catalogo = {provider.id for provider in default_providers()}

    assert set(nomes) >= ids_catalogo


def test_construtor_por_id_de_fornecedor() -> None:
    """build_adapter deve devolver um adaptador coerente ao fornecedor."""
    transporte = _TransporteRecorder((200, json.dumps({"models": []})))

    ollama = build_adapter(_definicao("ollama"), transporte)
    assert isinstance(ollama, RuntimeAdapter)
    assert ollama.name == "ollama"

    remoto = build_adapter(_definicao("openai_compatible"), transporte)
    assert isinstance(remoto, RuntimeAdapter)
    assert remoto.name == "openai_compatible"


def test_construtor_fornecedor_sem_adaptador() -> None:
    """Fornecedores sem adaptador devem falhar com AdapterError."""
    transporte = _TransporteRecorder((200, "{}"))
    desconhecido = ProviderDefinition(
        id="fornecedor-estranho",
        name="Desconhecido",
        description="Sem adaptador.",
        type=ProviderType.REMOTE_API,
        default_base_url="http://localhost:1",
    )

    try:
        build_adapter(desconhecido, transporte)
        assert False, "deveria lançar AdapterError"
    except AdapterError as exc:
        assert "fornecedor-estranho" in str(exc)


# ------------------------------------------------- transport HTTP (real)
class _HandlerAdaptador(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        corpo = json.dumps({"models": [{"name": "local-model"}]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_transporte_http_ajusta_orientado() -> None:
    """O transporte real deve devolver estado e corpo de um servidor local."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _HandlerAdaptador)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        status, body = http_json_transport(f"{base_url}/api/tags", "GET")
        assert status == 200
        assert json.loads(body) == {"models": [{"name": "local-model"}]}
    finally:
        server.shutdown()
        server.server_close()


def test_transporte_http_rede_inacessivel() -> None:
    """A falha de rede no transporte deve converter-se em AdapterError."""
    try:
        http_json_transport("http://127.0.0.1:1/api/tags", "GET", timeout=1.0)
        assert False, "deveria lançar AdapterError"
    except AdapterError as exc:
        assert "rede" in str(exc)


def test_adaptador_integrado_com_transporte_real() -> None:
    """Um adaptador com o transporte real deve funcionar contra o servidor."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _HandlerAdaptador)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        adaptador = build_adapter(
            _definicao("ollama"),
            http_json_transport,
        )
        modelos = adaptador.list_models(base_url)
        assert modelos == ("local-model",)
    finally:
        server.shutdown()
        server.server_close()