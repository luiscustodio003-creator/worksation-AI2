"""Endpoint de sistema da API (API-02).

Apresenta o use-case ``SystemInfoService`` (APP-03) sobre HTTP: transforma o
``SystemInfoResponse`` da camada Application num ``ApiResponse`` com payload
serializável em JSON (``platform`` + ``uptime``). O handler é um apresentador
fino — não contém lógica de domínio nem I/O próprio: delega a recolha no
serviço, que pode ser injectado para testes deterministas. Dependência
arquitectural: ``api -> application`` (fronteira sancionada).
"""

from __future__ import annotations

from wsai2.application import (
    SystemInfoRequest,
    SystemInfoResponse,
    SystemInfoService,
)

from .contract import ApiRequest, ApiResponse


def system(
    request: ApiRequest,
    service: SystemInfoService | None = None,
) -> ApiResponse:
    """Endpoint ``GET /system``: plataforma e uptime do sistema.

    Usa, por omissão, o ``SystemInfoService`` real (detecção do SO e do
    uptime corrente). Um serviço pode ser injectado para tornar o resultado
    determinista nos testes. O método/rota são validados pelo gateway; aqui
    assume-se ``GET /system`` já resolvido.
    """
    del request  # endpoint sem parâmetros de entrada (sinal puro)
    servico = service if service is not None else SystemInfoService()
    resposta: SystemInfoResponse = servico.resolve(SystemInfoRequest())

    plataforma = resposta.platform
    uptime = resposta.uptime
    return ApiResponse(
        status=200,
        payload={
            "platform": {
                "os": plataforma.os.value,
                "name": plataforma.name,
                "release": plataforma.release,
                "version": plataforma.version,
                "machine": plataforma.machine,
            },
            "uptime": {
                "boot_timestamp": uptime.boot_timestamp,
                "uptime_seconds": uptime.uptime_seconds,
                "uptime_hours": uptime.uptime_hours,
                "uptime_days": uptime.uptime_days,
            }
            if uptime is not None
            else None,
        },
    )