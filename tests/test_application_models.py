"""Testes do use-case Models (APP-07).

Verifica que ``ModelsService`` monta o ``ModelsResponse`` a partir de
``wsai2.model.evaluate_models`` (fontes injectáveis) e honra o filtro
opcional por categoria (``ModelsRequest.category``).
"""

from dataclasses import FrozenInstanceError

import pytest

from wsai2.application import ModelsRequest, ModelsResponse, ModelsService
from wsai2.capability import create_default_registry as create_capability_registry
from wsai2.hardware import discover_hardware
from wsai2.model import ModelCategory, ModelVerdict, create_default_registry
from wsai2.runtime import discover_runtime


def _servico_padrao() -> ModelsService:
    return ModelsService()


def test_resolve_padrao_devolve_veredictos() -> None:
    """APP-07: por omissão, o serviço avalia todos os modelos do registo."""
    resposta = _servico_padrao().resolve(ModelsRequest())
    assert isinstance(resposta, ModelsResponse)
    assert all(isinstance(v, ModelVerdict) for v in resposta.verdicts)
    assert len(resposta.verdicts) == len(create_default_registry())


def test_resolve_sem_categoria_nao_filtra() -> None:
    """APP-07: sem categoria, os veredictos cobrem todos os modelos."""
    resposta = _servico_padrao().resolve(ModelsRequest())
    ids = {verdict.model_id for verdict in resposta.verdicts}
    esperados = {definition.id for definition in create_default_registry().all()}
    assert ids == esperados


def test_resolve_por_categoria_chat() -> None:
    """APP-07: o filtro por categoria restringe os veredictos."""
    resposta = _servico_padrao().resolve(ModelsRequest(category=ModelCategory.CHAT))
    assert len(resposta.verdicts) > 0
    registo = create_default_registry()
    for verdict in resposta.verdicts:
        assert registo.get(verdict.model_id).category is ModelCategory.CHAT


def test_resolve_com_fontes_injectadas() -> None:
    """APP-07: fontes fixas controlam a avaliação devolvida."""
    registo = create_default_registry()
    hardware = discover_hardware()
    runtime = discover_runtime()
    servico = ModelsService(
        model_registry_source=lambda: registo,
        capability_registry_source=create_capability_registry,
        hardware_source=lambda: hardware,
        runtime_source=lambda: runtime,
    )
    resposta = servico.resolve(ModelsRequest())
    assert {v.model_id for v in resposta.verdicts} == {
        d.id for d in registo.all()
    }


def test_resposta_imutavel_a_contrato() -> None:
    """APP-07: a resposta respeita o contrato congelado (frozen dataclass)."""
    resposta = _servico_padrao().resolve(ModelsRequest())

    assert resposta == ModelsResponse(verdicts=resposta.verdicts)

    with pytest.raises(FrozenInstanceError):
        resposta.verdicts = ()