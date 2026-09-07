"""Testes dos health checks do Provider Layer.

Valida a avaliação da saúde fina dos fornecedores (endpoint + motor)
com probe e adaptador injectáveis, e a integração real com servidor
local, fechando a Fase 6.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from wsai2.provider import (
    AdapterError,
    ProviderDefinition,
    ProviderHealthStatus,
    ProviderRegistry,
    ProviderType,
    build_adapter,
    check_provider_health,
    check_providers_health,
    create_default_registry,
    default_providers,
    healthy_providers,
)
from wsai2.provider.adapters import RuntimeAdapter, TransportResult
from wsai2.provider.detection import ProviderProbeResult
from wsai2.provider.transports import http_json_transport


class _ProbeControl:
    """Probe injectável com resposta configurável."""

    def __init__(self, reachable: bool = True, error: str | None = None) -> None:
        self.reachable = reachable
        self.error = error
        self.chamadas: list[str] = []

    def __call__(self, base_url: str) -> ProviderProbeResult:
        self.chamadas.append(base_url)
        if not self.reachable:
            return ProviderProbeResult(
                reachable=False,
                error=self.error or "ligação recusada",
            )
        return ProviderProbeResult(reachable=True, latency_ms=7.5)


class _AdaptadorOK(RuntimeAdapter):
    """Adaptador de teste que responde com uma lista fixa."""

    name = "teste"

    def list_models(self, base_url: str) -> tuple[str, ...]:
        return ("modelo-a", "modelo-b")

    def generate(
        self,
        base_url: str,
        model_id: str,
        prompt: str,
        max_tokens: int = 256,
    ) -> str:
        return "resposta de teste"


class _AdaptadorQuebrado(_AdaptadorOK):
    """Adaptador de teste cujo motor falha ao listar modelos."""

    def list_models(self, base_url: str) -> tuple[str, ...]:
        raise AdapterError("o motor não conseguiu listar modelos")


def _harmonizar_registo() -> ProviderRegistry:
    registo = create_default_registry()
    registo.register(
        ProviderDefinition(
            id="sem-adaptador",
            name="Sem adaptador",
            description="Fornecedor sem adaptador registado.",
            type=ProviderType.REMOTE_API,
            default_base_url="http://localhost:1",
        )
    )
    return registo


def test_health_provider_endpoint_inacessivel() -> None:
    """Endpoint inacessível deve dar UNAVAILABLE sem contactar o motor."""
    definicao = default_providers()[0]
    probe = _ProbeControl(reachable=False)

    health = check_provider_health(definicao, probe, _AdaptadorOK())

    assert health.status is ProviderHealthStatus.UNAVAILABLE
    assert health.is_healthy is False
    assert health.model_count is None
    assert health.error == "ligação recusada"
    assert probe.chamadas == [definicao.default_base_url]


def test_health_provider_motor_degradado() -> None:
    """Endpoint acessível mas motor com falha deve dar DEGRADED."""
    definicao = default_providers()[0]

    health = check_provider_health(definicao, _ProbeControl(), _AdaptadorQuebrado())

    assert health.status is ProviderHealthStatus.DEGRADED
    assert health.is_healthy is False
    assert "motor" in str(health.error)
    assert health.model_count is None


def test_health_provider_saudavel() -> None:
    """Endpoint e motor a responder devem dar HEALTHY com contagem."""
    definicao = default_providers()[0]

    health = check_provider_health(definicao, _ProbeControl(), _AdaptadorOK())

    assert health.status is ProviderHealthStatus.HEALTHY
    assert health.is_healthy is True
    assert health.model_count == 2
    assert health.latency_ms == 7.5
    assert health.error is None


def test_health_base_url_personalizada() -> None:
    """Uma base_url indicada deve sobrepor-se à predefinida."""
    definicao = default_providers()[0]
    probe = _ProbeControl()

    health = check_provider_health(
        definicao,
        probe,
        _AdaptadorOK(),
        base_url="http://127.0.0.1:7777",
    )

    assert health.base_url == "http://127.0.0.1:7777"
    assert probe.chamadas == ["http://127.0.0.1:7777"]


def test_health_sumario() -> None:
    """O resumo deve reflectir o estado de saúde."""
    definicao = default_providers()[0]

    saudavel = check_provider_health(definicao, _ProbeControl(), _AdaptadorOK())
    fora = check_provider_health(
        definicao,
        _ProbeControl(reachable=False),
        _AdaptadorOK(),
    )

    assert saudavel.status.value in saudavel.summary
    assert fora.status.value in fora.summary


def _probe_por_base_url(base_url: str) -> ProviderProbeResult:
    if base_url == "http://127.0.0.1:8801":
        return ProviderProbeResult(reachable=True, latency_ms=3.0)
    return ProviderProbeResult(reachable=False, error="sem resposta")


def _transporte_tags_um(url: str, method: str, payload: object | None) -> TransportResult:
    """Transport injectável que responde como se o motor tivesse 1 modelo."""
    return (200, json.dumps({"models": [{"name": "real-model"}]}))


def _transporte_tags_dois(url: str, method: str, payload: object | None) -> TransportResult:
    """Transport injectável que responde como se o motor tivesse 2 modelos."""
    return (200, json.dumps({"models": [{"name": "a"}, {"name": "b"}]}))


def test_health_registo_ordem_e_estados() -> None:
    """O health check do registo combina estados por fornecedor."""
    registo = create_default_registry()

    results = check_providers_health(
        registo,
        _probe_por_base_url,
        _transporte_tags_um,
        base_urls={
            "ollama": "http://127.0.0.1:8801",
            "openai_compatible": "http://127.0.0.1:8802",
        },
    )

    assert [result.provider_id for result in results] == [
        "llama_cpp",
        "ollama",
        "openai_compatible",
    ]
    por_id = {result.provider_id: result for result in results}
    assert por_id["ollama"].status is ProviderHealthStatus.HEALTHY
    assert por_id["llama_cpp"].status is ProviderHealthStatus.UNAVAILABLE
    assert por_id["openai_compatible"].status is ProviderHealthStatus.UNAVAILABLE


def test_health_registo_constroi_adaptadores() -> None:
    """check_providers_health deve construir adaptadores por id."""
    registo = _harmonizar_registo()

    def probe(base_url: str) -> ProviderProbeResult:
        return ProviderProbeResult(reachable=True, latency_ms=4.0)

    results = check_providers_health(
        registo,
        probe,
        _transporte_tags_um,
        base_urls={"sem-adaptador": "http://127.0.0.1:1"},
    )

    por_id = {result.provider_id: result for result in results}
    assert por_id["ollama"].status is ProviderHealthStatus.HEALTHY
    assert por_id["sem-adaptador"].status is ProviderHealthStatus.DEGRADED
    assert "Nenhum adaptador" in str(por_id["sem-adaptador"].error)
    assert por_id["sem-adaptador"].is_healthy is False


def test_health_saudaveis_filtram() -> None:
    """healthy_providers deve devolver apenas os saudáveis."""
    definicao = default_providers()[0]

    saudavel = check_provider_health(definicao, _ProbeControl(), _AdaptadorOK())
    degradado = check_provider_health(definicao, _ProbeControl(), _AdaptadorQuebrado())
    fora = check_provider_health(
        definicao,
        _ProbeControl(reachable=False),
        _AdaptadorOK(),
    )

    resultados = (saudavel, degradado, fora)
    assert [result.provider_id for result in healthy_providers(resultados)] == [
        "ollama"
    ]


class _HandlerHealth(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        corpo = json.dumps({"models": [{"name": "real-model"}]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, format: str, *args: object) -> None:
        return


def test_health_integrado_servidor_local() -> None:
    """Health check real: probe HTTP + adaptador + transporte contra servidor."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), _HandlerHealth)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}"
        from wsai2.provider import health as health_mod
        from wsai2.provider.probes import health_probe

        resultados = check_providers_health(
            create_default_registry(),
            health_probe,
            http_json_transport,
            base_urls={"ollama": base_url},
        )
        por_id = {result.provider_id: result for result in resultados}
        assert por_id["ollama"].status is ProviderHealthStatus.HEALTHY
        assert por_id["ollama"].model_count == 1
        assert por_id["ollama"].is_healthy is True
    finally:
        server.shutdown()
        server.server_close()


def test_health_full_cycle_sem_adaptador() -> None:
    """O registo completo deve incluir fornecedores sem adaptador."""
    registo = _harmonizar_registo()

    def probe(base_url: str) -> ProviderProbeResult:
        return ProviderProbeResult(reachable=True, latency_ms=2.0)

    resultados = check_providers_health(registo, probe, _transporte_tags_dois)
    por_id = {result.provider_id: result for result in resultados}

    assert len(resultados) == len(registo)
    assert por_id["ollama"].status is ProviderHealthStatus.HEALTHY
    assert por_id["ollama"].model_count == 2
    assert por_id["sem-adaptador"].status is ProviderHealthStatus.DEGRADED
    assert por_id["sem-adaptador"].is_healthy is False