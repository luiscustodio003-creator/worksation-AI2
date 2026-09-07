"""Testes da detecção de fornecedores do Provider Layer.

Valida a lógica de domínio da detecção com probes injectáveis
determinísticos e o probe HTTP real contra um servidor local.
"""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from wsai2.provider import (
    ProviderDefinition,
    ProviderDetection,
    ProviderProbeResult,
    ProviderRegistry,
    ProviderType,
    available_providers,
    create_default_registry,
    detect_provider,
    detect_providers,
    default_providers,
)
from wsai2.provider.detection import ProviderProbe
from wsai2.provider.probes import health_probe


def _definicao_ollama() -> ProviderDefinition:
    return next(
        provider
        for provider in default_providers()
        if provider.id == "ollama"
    )


def _probe_sucesso(base_url: str) -> ProviderProbeResult:
    return ProviderProbeResult(reachable=True, latency_ms=12.0)


def _probe_falha(base_url: str) -> ProviderProbeResult:
    return ProviderProbeResult(reachable=False, error="ligação recusada")


def test_detectar_provider_sucesso() -> None:
    """Um probe de sucesso deve marcar o fornecedor como acessível."""
    detection = detect_provider(_definicao_ollama(), _probe_sucesso)

    assert isinstance(detection, ProviderDetection)
    assert detection.provider_id == "ollama"
    assert detection.reachable is True
    assert detection.latency_ms == 12.0
    assert detection.error is None


def test_detectar_provider_falha() -> None:
    """Um probe de falha deve marcar o fornecedor como inacessível."""
    detection = detect_provider(_definicao_ollama(), _probe_falha)

    assert detection.reachable is False
    assert detection.error == "ligação recusada"


def test_detectar_provider_usa_base_url_predefinida() -> None:
    """Sem base_url indicada, deve ser usada a da definição."""
    detection = detect_provider(_definicao_ollama(), _probe_sucesso)

    assert detection.base_url == _definicao_ollama().default_base_url


def test_detectar_provider_base_url_personalizada() -> None:
    """Uma base_url indicada deve sobrepor-se à predefinida."""
    detection = detect_provider(
        _definicao_ollama(),
        _probe_sucesso,
        base_url="http://127.0.0.1:9999",
    )

    assert detection.base_url == "http://127.0.0.1:9999"


def test_detectar_provider_propaga_capacidades() -> None:
    """As capacidades declaradas devem ser propagadas à detecção."""
    detection = detect_provider(_definicao_ollama(), _probe_sucesso)

    assert detection.capabilities_provided == (
        "local_llm_inference",
        "local_embeddings",
    )


def test_detectar_provider_sumario() -> None:
    """O resumo deve indicar o estado de acessibilidade."""
    sucesso = detect_provider(_definicao_ollama(), _probe_sucesso)
    falha = detect_provider(_definicao_ollama(), _probe_falha)

    assert "disponível" in sucesso.summary
    assert "indisponível" in falha.summary


def test_detectar_providers_ordem_por_id() -> None:
    """A detecção do registo deve devolver resultados ordenados por id."""
    registry = create_default_registry()
    detections = detect_providers(registry, _probe_sucesso)

    assert len(detections) == len(registry)
    ids = [detection.provider_id for detection in detections]
    assert ids == sorted(ids)


def test_detectar_providers_com_overrides() -> None:
    """Os overrides de base_url devem ser aplicados por fornecedor."""
    registry = create_default_registry()
    overrides = {"ollama": "http://127.0.0.1:4321"}
    detections = detect_providers(registry, _probe_sucesso, base_urls=overrides)

    por_id = {detection.provider_id: detection for detection in detections}
    assert por_id["ollama"].base_url == "http://127.0.0.1:4321"


def test_disponiveis_filtra_por_acessibilidade() -> None:
    """available_providers deve devolver apenas os acessíveis."""

    def probe_misto(base_url: str) -> ProviderProbeResult:
        if base_url == "http://127.0.0.1:4444":
            return ProviderProbeResult(reachable=True)
        return ProviderProbeResult(reachable=False, error="ligação recusada")

    registry = ProviderRegistry(
        (
            ProviderDefinition(
                id="fornecedor-on",
                name="Fornecedor ON",
                description="Teste.",
                type=ProviderType.LOCAL_RUNTIME,
                default_base_url="http://127.0.0.1:4444",
            ),
            ProviderDefinition(
                id="fornecedor-off",
                name="Fornecedor OFF",
                description="Teste.",
                type=ProviderType.LOCAL_RUNTIME,
                default_base_url="http://127.0.0.1:5555",
            ),
        )
    )

    detections = detect_providers(registry, probe_misto)
    disponiveis = available_providers(detections)

    assert [disponivel.provider_id for disponivel in disponiveis] == [
        "fornecedor-on"
    ]


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def test_probe_http_servidor_local() -> None:
    """O probe HTTP deve detectar um servidor local a responder."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        result = health_probe(base_url)

        assert result.reachable is True
        assert result.error is None
        assert result.latency_ms is not None
        assert result.latency_ms >= 0.0
    finally:
        server.shutdown()
        server.server_close()


def test_probe_http_porta_fechada() -> None:
    """O probe HTTP deve falhar quando o endpoint não responde."""
    result = health_probe("http://127.0.0.1:1")

    assert result.reachable is False
    assert result.error is not None