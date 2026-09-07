"""Probes concretas para detecção de fornecedores.

Código de I/O de rede (dependente do ambiente), separado da lógica de
domínio em `detection.py` (constituição arquitectural, artigo 5). A
detecção usa estas probes apenas através da assinatura `ProviderProbe`.
"""

from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request


class ProviderProbeError(Exception):
    """Erro na execução de um probe de fornecedor."""


def health_probe(base_url: str, timeout: float = 2.0) -> "ProviderProbeResult":
    """Contacta o endpoint base de um fornecedor via HTTP.

    Devolve um `ProviderProbeResult` com a acessibilidade, a latência em
    milissegundos e, em caso de falha, uma mensagem de erro descritiva.

    O contacto é razoavelmente tolerante: qualquer resposta HTTP válida
    (incluindo códigos de erro do servidor) conta como fornecedor
    presente — a saúde fina cuidada pelos health checks.
    """
    from .detection import ProviderProbeResult

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(base_url, timeout=timeout) as _:
            latency_ms = (time.perf_counter() - start) * 1000.0
        return ProviderProbeResult(reachable=True, latency_ms=latency_ms)
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
        latency_ms = (time.perf_counter() - start) * 1000.0
        return ProviderProbeResult(
            reachable=False,
            latency_ms=latency_ms,
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 — agrupar falhas imprevistas do probe
        latency_ms = (time.perf_counter() - start) * 1000.0
        return ProviderProbeResult(
            reachable=False,
            latency_ms=latency_ms,
            error=f"falha imprevista: {exc!r}",
        )


__all__ = ["ProviderProbeError", "health_probe"]