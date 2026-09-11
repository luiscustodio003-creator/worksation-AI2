"""Endpoint de modelos da API (API-06).

Apresenta o use-case ``ModelsService`` (APP-07) sobre HTTP: transforma o
``ModelsResponse`` da camada Application num ``ApiResponse`` com payload
serializável em JSON (veredictos de compatibilidade dos modelos contra o
hardware, o runtime e as capacidades do sistema). O handler é um
apresentador fino — não contém lógica de domínio nem I/O próprio: delega
a recolha no serviço, que pode ser injectado para testes deterministas.
Dependência arquitectural: ``api -> application``.
"""

from __future__ import annotations

from wsai2.application import ModelsRequest, ModelsResponse, ModelsService

from .contract import ApiRequest, ApiResponse


def models(
    request: ApiRequest,
    service: ModelsService | None = None,
) -> ApiResponse:
    """Endpoint ``GET /models``: veredictos de compatibilidade dos modelos.

    Usa, por omissão, o ``ModelsService`` real (registos e fontes de
    hardware/runtime reais). Um serviço pode ser injectado para tornar o
    resultado determinista nos testes. O método/rota são validados pelo
    gateway; aqui assume-se ``GET /models`` já resolvido.
    """
    del request  # endpoint de leitura sem parâmetros de entrada
    servico = service if service is not None else ModelsService()
    resposta: ModelsResponse = servico.resolve(ModelsRequest())
    return ApiResponse(status=200, payload=_veredictos_para_payload(resposta))


def _veredictos_para_payload(resposta: ModelsResponse) -> dict[str, object]:
    """Serializa os ``ModelVerdict`` do contrato em JSON puro."""
    veredictos = resposta.verdicts
    contagens = {
        "available": sum(1 for v in veredictos if v.state.value == "available"),
        "restricted": sum(1 for v in veredictos if v.state.value == "restricted"),
        "unavailable": sum(1 for v in veredictos if v.state.value == "unavailable"),
    }
    return {
        "summary": (
            f"{len(veredictos)} modelos, {contagens['available']} disponíveis, "
            f"{contagens['restricted']} condicionados, "
            f"{contagens['unavailable']} indisponíveis"
        ),
        "counts": contagens,
        "verdicts": [
            {
                "model_id": veredicto.model_id,
                "state": veredicto.state.value,
                "is_available": veredicto.is_available,
                "summary": veredicto.summary,
                "checks": [
                    {
                        "name": check.name,
                        "required": _valor_json(check.required),
                        "available": _valor_json(check.available),
                        "satisfied": check.satisfied,
                    }
                    for check in veredicto.checks
                ],
                "missing_capabilities": list(veredicto.missing_capabilities),
            }
            for veredicto in veredictos
        ],
    }


def _valor_json(valor: object) -> object:
    """Converte tuplas em listas (JSON) e devolve os restantes valores."""
    if isinstance(valor, tuple):
        return list(valor)
    return valor