"""Adaptadores de runtime para os fornecedores concretos.

Define a interface estável de comunicação com os motores concretos
(listar modelos, gerar texto) atrás de um contrato único
(`RuntimeAdapter`). Tal como na detecção, o I/O é injectável: cada
adaptador recebe um *transport* (`Transport`) que executa a chamada
HTTP; assim a lógica de cada adaptador é testável sem rede.

Os transports concretos vivem em `transports.py`; este módulo apenas os
invoca através da assinatura injectada.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Protocol, runtime_checkable

from .base import ProviderDefinition

# (status_code, body_text) — resultado bruto de uma chamada HTTP.
TransportResult = tuple[int, str]

# Transporte HTTP injectável: (url, method, payload | None) -> resultado.
Transport = Callable[[str, str, object | None], TransportResult]

_UNKNOWN_PROVIDER = "Nenhum adaptador registado para o fornecedor '{0}'."


class AdapterError(Exception):
    """Erro de comunicação ou de resposta de um adaptador."""


@runtime_checkable
class RuntimeAdapter(Protocol):
    """Contrato estável de comunicação com um runtime de inferência."""

    name: str

    def list_models(self, base_url: str) -> tuple[str, ...]:
        """Lista os modelos disponíveis no runtime."""
        ...

    def generate(
        self,
        base_url: str,
        model_id: str,
        prompt: str,
        max_tokens: int = 256,
    ) -> str:
        """Gera texto para o modelo indicado a partir do prompt."""
        ...


def _parse_json_body(status: int, body_text: str) -> object:
    """Converte o corpo textual numa estrutura JSON ou falha com erro."""
    if status >= 400:
        raise AdapterError(f"o fornecedor respondeu com o estado HTTP {status}")
    try:
        return json.loads(body_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise AdapterError(f"resposta JSON inválida do fornecedor: {exc}") from exc


class OllamaAdapter:
    """Adaptador para o runtime local Ollama (protocolo nativo)."""

    name = "ollama"

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def list_models(self, base_url: str) -> tuple[str, ...]:
        """Lista os modelos via ``GET /api/tags``."""
        url = f"{base_url.rstrip('/')}/api/tags"
        status, body_text = self._transport(url, "GET", None)
        data = _parse_json_body(status, body_text)
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            raise AdapterError("resposta /api/tags sem campo 'models'")
        return tuple(model.get("name", "") for model in data["models"] if isinstance(model, dict))

    def generate(
        self,
        base_url: str,
        model_id: str,
        prompt: str,
        max_tokens: int = 256,
    ) -> str:
        """Gera texto via ``POST /api/generate`` (stream desactivado)."""
        url = f"{base_url.rstrip('/')}/api/generate"
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        status, body_text = self._transport(url, "POST", payload)
        data = _parse_json_body(status, body_text)
        if not isinstance(data, dict) or not isinstance(data.get("response"), str):
            raise AdapterError("resposta /api/generate sem campo 'response'")
        return data["response"]


class OpenAiCompatibleAdapter:
    """Adaptador para runtimes compatíveis com a API OpenAI."""

    name = "openai_compatible"

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def list_models(self, base_url: str) -> tuple[str, ...]:
        """Lista os modelos via ``GET /v1/models``."""
        url = f"{base_url.rstrip('/')}/v1/models"
        status, body_text = self._transport(url, "GET", None)
        data = _parse_json_body(status, body_text)
        if not isinstance(data, dict) or not isinstance(data.get("data"), list):
            raise AdapterError("resposta /v1/models sem campo 'data'")
        return tuple(str(model.get("id", "")) for model in data["data"] if isinstance(model, dict))

    def generate(
        self,
        base_url: str,
        model_id: str,
        prompt: str,
        max_tokens: int = 256,
    ) -> str:
        """Gera texto via ``POST /v1/chat/completions``."""
        url = f"{base_url.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        status, body_text = self._transport(url, "POST", payload)
        data = _parse_json_body(status, body_text)
        try:
            content = data["choices"][0]["message"]["content"]  # type: ignore[index]
        except (KeyError, IndexError, TypeError) as exc:
            raise AdapterError("resposta chat/completions sem conteúdo") from exc
        if not isinstance(content, str):
            raise AdapterError("conteúdo de resposta não textual")
        return content


_ADAPTER_FACTORIES: dict[str, Callable[[Transport], RuntimeAdapter]] = {
    "ollama": OllamaAdapter,
    "llama_cpp": OpenAiCompatibleAdapter,
    "openai_compatible": OpenAiCompatibleAdapter,
}


def adapter_factory_names() -> tuple[str, ...]:
    """Ids de fornecedores com adaptador registado, ordenados."""
    return tuple(sorted(_ADAPTER_FACTORIES))


def build_adapter(
    definition: ProviderDefinition,
    transport: Transport,
) -> RuntimeAdapter:
    """Constrói o adaptador adequado à definição de fornecedor.

    A escolha do adaptador é feita por id do fornecedor no catálogo de
    adaptadores. Lança ``AdapterError`` quando não existe adaptador para
    o fornecedor.
    """
    factory = _ADAPTER_FACTORIES.get(definition.id)
    if factory is None:
        raise AdapterError(_UNKNOWN_PROVIDER.format(definition.id))
    return factory(transport)


__all__ = [
    "AdapterError",
    "OllamaAdapter",
    "OpenAiCompatibleAdapter",
    "RuntimeAdapter",
    "Transport",
    "TransportResult",
    "adapter_factory_names",
    "build_adapter",
]