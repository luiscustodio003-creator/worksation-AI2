"""Transports HTTP concretos para os adaptadores de runtime.

Código de I/O de rede (dependente do ambiente), separado da lógica de
domínio em `adapters.py` (constituição arquitectural, artigo 5). Os
adaptadores usam estes transports apenas através da assinatura
`Transport`.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

from . import adapters


def http_json_transport(
    url: str,
    method: str,
    payload: object | None = None,
    timeout: float = 10.0,
) -> adapters.TransportResult:
    """Executa uma chamada HTTP JSON e devolve ``(status, corpo texto)``.

    Para métodos a enviar corpo (ex.: POST), o payload é serializado
    para JSON; o conteúdo enviado e pedido usa JSON (application/json).
    Falhas de rede convertem-se em ``AdapterError``.
    """
    data: bytes | None = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
        raise adapters.AdapterError(f"falha de rede ao contactar o fornecedor: {exc}") from exc


__all__ = ["http_json_transport"]