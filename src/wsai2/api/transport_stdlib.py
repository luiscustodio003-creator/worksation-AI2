"""Transporte HTTP padrão do subsistema API (API-01).

Adapter de ``ApiGateway`` baseado apenas em ``http.server`` da biblioteca
standard (sem dependências externas). Converte pedidos HTTP em
``ApiRequest``, encaminha para a tabela de rotas e devolve ``ApiResponse``
como JSON. A substituição futura por outro transporte (ex.: ASGI) é feita
por novo adapter, sem tocar nos handlers.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Callable, Dict, Optional, Tuple

from .base import ApiGateway, health
from .contract import ApiRequest, ApiResponse
from .hardware import hardware
from .system import system

_ROTA_METODOS: Dict[str, frozenset[str]] = {
    "/health": frozenset({"GET"}),
    "/system": frozenset({"GET"}),
    "/hardware": frozenset({"GET"}),
}

_HANDLERS: Dict[str, Callable[[ApiRequest], ApiResponse]] = {
    "/health": health,
    "/system": system,
    "/hardware": hardware,
}


class StdLibHttpGateway(ApiGateway):
    """Gateway HTTP injectável implementado com ``http.server``.

    ``handle`` resolve a rota e o método a partir da tabela de rotas e
    delega no handler registado; pedidos com rota/método desconhecidos são
    rejeitados antes de qualquer handler (404/405).
    """

    def __init__(
        self,
        rotas: Optional[Dict[str, Tuple[frozenset[str], Callable[[ApiRequest], ApiResponse]]]] = None,
    ) -> None:
        if rotas is None:
            rotas = {rota: (_ROTA_METODOS[rota], _HANDLERS[rota]) for rota in _ROTA_METODOS}
        self._rotas: Dict[str, Tuple[frozenset[str], Callable[[ApiRequest], ApiResponse]]] = dict(rotas)
        self._lock = Lock()
        self._servidor: Optional[ThreadingHTTPServer] = None

    def handle(self, request: ApiRequest) -> ApiResponse:
        registo = self._rotas.get(request.path)
        if registo is None:
            return ApiResponse(status=404, payload={"error": "rota inexistente"})
        metodos, handler = registo
        if request.method not in metodos:
            return ApiResponse(
                status=405,
                payload={"error": "metodo nao suportado nesta rota"},
            )
        return handler(request)

    def serve(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> Tuple[str, int]:
        """Inicia o servidor em ``host:port`` (porta 0 = efémera).

        Devolve o par ``(host, port)`` efectivo para uso pelos clientes.
        O servidor corre em background até ``shutdown()`` ser chamado.
        """
        with self._lock:
            if self._servidor is not None:
                raise RuntimeError("gw: servidor já em execução")

            servidor = ThreadingHTTPServer((host, port), _PedidoHttp)
            servidor.daemon_threads = True
            servidor._gw = self
            self._servidor = servidor

        import threading

        threading.Thread(
            target=servidor.serve_forever,
            kwargs={"poll_interval": 0.05},
            daemon=True,
        ).start()
        host_real, port_real = servidor.server_address[:2]
        return host_real, int(port_real)

    def shutdown(self) -> None:
        """Termina o servidor, se estiver em execução, e limpa o estado."""
        with self._lock:
            servidor, self._servidor = self._servidor, None
        if servidor is not None:
            servidor.shutdown()
            servidor.server_close()


class _PedidoHttp(BaseHTTPRequestHandler):
    """Adapta cada pedido HTTP ao gateway e serializa a resposta em JSON."""

    def _processar(self) -> None:
        gateway: StdLibHttpGateway = self.server._gw  # type: ignore[attr-defined]
        comprimento = int(self.headers.get("Content-Length", "0") or "0")
        corpo = self.rfile.read(comprimento).decode("utf-8", errors="replace")
        pedido = ApiRequest(
            method=self.command,
            path=self.path.split("?", 1)[0],
            headers={chave: valor for chave, valor in self.headers.items()},
            body=corpo,
        )
        resposta = gateway.handle(pedido)
        corpo_json = json.dumps(resposta.payload).encode("utf-8")
        self.send_response(resposta.status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo_json)))
        for chave, valor in resposta.headers.items():
            self.send_header(chave, valor)
        self.end_headers()
        self.wfile.write(corpo_json)

    do_GET = _processar
    do_POST = _processar
    do_PUT = _processar
    do_DELETE = _processar
    do_PATCH = _processar
    do_HEAD = _processar

    def log_message(self, *_: object) -> None:
        """Silencia o log por pedido (a observabilidade é por monitorização)."""
        return