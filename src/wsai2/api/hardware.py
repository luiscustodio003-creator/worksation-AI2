"""Endpoint de hardware da API (API-03).

Apresenta o use-case ``HardwareProfileService`` (APP-04) sobre HTTP:
transforma o ``HardwareProfileResponse`` da camada Application num
``ApiResponse`` com payload serializável em JSON (perfil estrutural:
cpu, memória, gpus, armazenamento e capacidades derivadas). O handler é
um apresentador fino — não contém lógica de domínio nem I/O próprio:
delega a recolha no serviço, que pode ser injectado para testes
deterministas. Dependência arquitectural: ``api -> application``.
"""

from __future__ import annotations

from wsai2.application import (
    HardwareProfileRequest,
    HardwareProfileResponse,
    HardwareProfileService,
)

from .contract import ApiRequest, ApiResponse


def hardware(
    request: ApiRequest,
    service: HardwareProfileService | None = None,
) -> ApiResponse:
    """Endpoint ``GET /hardware``: perfil estrutural da máquina.

    Usa, por omissão, o ``HardwareProfileService`` real (descoberta do
    hardware). Um serviço pode ser injectado para tornar o resultado
    determinista nos testes. O método/rota são validados pelo gateway;
    aqui assume-se ``GET /hardware`` já resolvido.
    """
    del request  # endpoint sem parâmetros de entrada (sinal puro)
    servico = service if service is not None else HardwareProfileService()
    resposta: HardwareProfileResponse = servico.resolve(HardwareProfileRequest())
    return ApiResponse(status=200, payload=_perfil_para_payload(resposta))


def _perfil_para_payload(resposta: HardwareProfileResponse) -> dict[str, object]:
    """Serializa o ``HardwareProfile`` do contrato em JSON puro."""
    perfil = resposta.profile
    return {
        "overall_level": perfil.overall_level.value,
        "cpu_summary": perfil.cpu_summary,
        "memory_summary": perfil.memory_summary,
        "gpu_summary": perfil.gpu_summary,
        "storage_summary": perfil.storage_summary,
        "cpu": {
            "vendor": perfil.cpu.vendor.value,
            "model_name": perfil.cpu.model_name,
            "architecture": perfil.cpu.architecture.value,
            "physical_cores": perfil.cpu.physical_cores,
            "logical_cores": perfil.cpu.logical_cores,
            "max_frequency_mhz": perfil.cpu.max_frequency_mhz,
            "cache_l1_kb": perfil.cpu.cache_l1_kb,
            "cache_l2_kb": perfil.cpu.cache_l2_kb,
            "cache_l3_kb": perfil.cpu.cache_l3_kb,
            "features": list(perfil.cpu.features),
            "has_hyperthreading": perfil.cpu.has_hyperthreading,
        },
        "memory": {
            "total_bytes": perfil.memory.total_bytes,
            "total_gb": perfil.memory.total_gb,
            "swap_total_bytes": perfil.memory.swap_total_bytes,
            "swap_total_gb": perfil.memory.swap_total_gb,
            "has_swap": perfil.memory.has_swap,
        },
        "gpus": [
            {
                "name": gpu.name,
                "vendor": gpu.vendor,
                "vram_bytes": gpu.vram_bytes,
                "driver_version": gpu.driver_version,
            }
            for gpu in perfil.gpus
        ],
        "storage": [
            {
                "device_path": disco.device_path,
                "total_bytes": disco.total_bytes,
                "type": disco.type,
                "mount_point": disco.mount_point,
            }
            for disco in perfil.storage
        ],
        "capabilities": [
            {
                "domain": capacidade.domain.value,
                "score": capacidade.score,
                "level": capacidade.level.value,
                "details": capacidade.details,
            }
            for capacidade in perfil.capabilities
        ],
    }