"""Endpoint de runtime da API (API-04).

Apresenta o use-case ``RuntimeProfileService`` (APP-05) sobre HTTP:
transforma o ``RuntimeProfileResponse`` da camada Application num
``ApiResponse`` com payload serializável em JSON (estado momentâneo:
carga de CPU, memória, processos, uptime e disponibilidade efectiva).
O handler é um apresentador fino — não contém lógica de domínio nem I/O
próprio: delega a recolha no serviço, que pode ser injectado para testes
deterministas. Dependência arquitectural: ``api -> application``.
"""

from __future__ import annotations

from wsai2.application import (
    RuntimeProfileRequest,
    RuntimeProfileResponse,
    RuntimeProfileService,
)

from .contract import ApiRequest, ApiResponse


def runtime(
    request: ApiRequest,
    service: RuntimeProfileService | None = None,
) -> ApiResponse:
    """Endpoint ``GET /runtime``: estado momentâneo dos recursos.

    Usa, por omissão, o ``RuntimeProfileService`` real (descoberta do
    estado de runtime). Um serviço pode ser injectado para tornar o
    resultado determinista nos testes. O método/rota são validados pelo
    gateway; aqui assume-se ``GET /runtime`` já resolvido.
    """
    del request  # endpoint sem parâmetros de entrada (sinal puro)
    servico = service if service is not None else RuntimeProfileService()
    resposta: RuntimeProfileResponse = servico.resolve(RuntimeProfileRequest())
    return ApiResponse(status=200, payload=_perfil_para_payload(resposta))


def _perfil_para_payload(resposta: RuntimeProfileResponse) -> dict[str, object]:
    """Serializa o ``RuntimeProfile`` do contrato em JSON puro."""
    perfil = resposta.profile
    topo = perfil.top_process
    uptime = perfil.uptime
    return {
        "overall_status": perfil.overall_status.value,
        "cpu_summary": perfil.cpu_summary,
        "memory_summary": perfil.memory_summary,
        "uptime_summary": perfil.uptime_summary,
        "availability_summary": perfil.availability_summary,
        "cpu": {
            "percent": perfil.cpu.percent,
            "per_core": list(perfil.cpu.per_core),
            "count": perfil.cpu.count,
            "frequency_current_mhz": perfil.cpu.frequency_current_mhz,
            "is_idle": perfil.cpu.is_idle,
            "is_saturated": perfil.cpu.is_saturated,
        },
        "memory": {
            "total_bytes": perfil.memory.total_bytes,
            "available_bytes": perfil.memory.available_bytes,
            "used_bytes": perfil.memory.used_bytes,
            "percent": perfil.memory.percent,
            "swap_total_bytes": perfil.memory.swap_total_bytes,
            "swap_used_bytes": perfil.memory.swap_used_bytes,
            "swap_percent": perfil.memory.swap_percent,
            "free_percent": perfil.memory.free_percent,
            "has_swap_active": perfil.memory.has_swap_active,
        },
        "processes": [
            {
                "pid": processo.pid,
                "name": processo.name,
                "status": processo.status,
                "cpu_percent": processo.cpu_percent,
                "memory_rss_bytes": processo.memory_rss_bytes,
                "memory_percent": processo.memory_percent,
            }
            for processo in perfil.processes
        ],
        "uptime": {
            "boot_timestamp": uptime.boot_timestamp,
            "uptime_seconds": uptime.uptime_seconds,
            "uptime_hours": uptime.uptime_hours,
            "uptime_days": uptime.uptime_days,
        }
        if uptime is not None
        else None,
        "availability": [
            {
                "domain": disp.domain.value,
                "score": disp.score,
                "status": disp.status.value,
                "details": disp.details,
            }
            for disp in perfil.availability
        ],
        "top_process": {
            "pid": topo.pid,
            "name": topo.name,
            "status": topo.status,
            "cpu_percent": topo.cpu_percent,
            "memory_rss_bytes": topo.memory_rss_bytes,
            "memory_percent": topo.memory_percent,
        }
        if topo is not None
        else None,
    }