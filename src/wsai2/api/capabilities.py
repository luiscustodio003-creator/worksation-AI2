"""Endpoint de capacidades da API (API-05).

Apresenta o use-case ``CapabilitiesService`` (APP-06) sobre HTTP:
transforma o ``CapabilitiesResponse`` da camada Application num
``ApiResponse`` com payload serializável em JSON (catálogo de
capacidades avaliadas contra o hardware e o runtime actuais — estado,
justificação e verificação por requisito). O handler é um apresentador
fino — não contém lógica de domínio nem I/O próprio: delega a recolha no
serviço, que pode ser injectado para testes deterministas. Dependência
arquitectural: ``api -> application``.
"""

from __future__ import annotations

from wsai2.application import (
    CapabilitiesRequest,
    CapabilitiesResponse,
    CapabilitiesService,
)

from .contract import ApiRequest, ApiResponse


def capabilities(
    request: ApiRequest,
    service: CapabilitiesService | None = None,
) -> ApiResponse:
    """Endpoint ``GET /capabilities``: capacidades disponíveis no sistema.

    Usa, por omissão, o ``CapabilitiesService`` real (registo padrão,
    hardware e runtime reais). Um serviço pode ser injectado para tornar
    o resultado determinista nos testes. O método/rota são validados pelo
    gateway; aqui assume-se ``GET /capabilities`` já resolvido.
    """
    del request  # endpoint de leitura sem parâmetros de entrada
    servico = service if service is not None else CapabilitiesService()
    resposta: CapabilitiesResponse = servico.resolve(CapabilitiesRequest())
    return ApiResponse(status=200, payload=_relatorio_para_payload(resposta))


def _relatorio_para_payload(resposta: CapabilitiesResponse) -> dict[str, object]:
    """Serializa o ``CompatibilityReport`` do contrato em JSON puro."""
    relatorio = resposta.report
    return {
        "summary": relatorio.summary,
        "counts": {
            "available": len(relatorio.available),
            "restricted": len(relatorio.restricted),
            "unavailable": len(relatorio.unavailable),
        },
        "entries": [
            {
                "id": entrada.definition.id,
                "name": entrada.definition.name,
                "description": entrada.definition.description,
                "domain": entrada.definition.domain.value,
                "state": entrada.state.value,
                "is_available": entrada.is_available,
                "justification": entrada.justification,
                "requirements": {
                    "min_ram_gb": entrada.definition.requirements.min_ram_gb,
                    "min_vram_gb": entrada.definition.requirements.min_vram_gb,
                    "min_cpu_cores": entrada.definition.requirements.min_cpu_cores,
                    "requires_gpu": entrada.definition.requirements.requires_gpu,
                    "min_available_disk_gb":
                        entrada.definition.requirements.min_available_disk_gb,
                },
                "checks": [
                    {
                        "name": check.name,
                        "required": check.required,
                        "available": check.available,
                        "satisfied": check.satisfied,
                    }
                    for check in entrada.verdict.checks
                ],
            }
            for entrada in relatorio.entries
        ],
    }