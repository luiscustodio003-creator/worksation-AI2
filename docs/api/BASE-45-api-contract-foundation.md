# WORKSTATION AI 2 — BASE-45: API — FUNDAÇÃO DO SUBSISTEMA (contrato + transporte stdlib)

## Responsabilidade

Camada Application do WSAI 2 (subsistema `wsai2.api`, arquitectura 3.10):
expor **capacidades reais do sistema através de contratos estáveis**, sem
carregar lógica central de negócio. A API é consumidora do kernel e dos
subsistemas de domínio exclusivamente pelas suas superfícies públicas.

Esta base cobre a fundação (unidade API-01): o contrato de mensagens, o
porte de transporte injectável e um endpoint de exemplo (`/health`), por
trás de um adapter stdlib sem dependências externas.

## Âmbito (API-01)

- Contrato puro de mensagens: `ApiRequest`/`ApiResponse` (imutáveis).
- Porte `ApiGateway` (interface de transporte injectável).
- Adapter `StdLibHttpGateway` (transporte `http.server`; JSON; 404/405
  antes de qualquer handler).
- Serviço de exemplo `health` (versões de contrato API/core; sem domínio).
- Autorização de `api` na fonte única: sai de `SUBSISTEMAS_FUTUROS`;
  `FIREWALL["api"] = {"core"}`; aresta `FRONTEIRAS ("api","core")`;
  `SUPERFICIES_PUBLICAS["api"]` + `API_CONTRACT_VERSION = "1.0"`.

**Fora do âmbito (unidades seguintes):** recursos de domínio
(system/hardware/runtime/capabilities/models/tasks/knowledge), autenticação,
rate limiting e outros transportes.

## Dependências

- `api → core` (via `wsai2.core.public`, regra KERNEL-08); nenhuma
  biblioteca externa (stdlib `http.server`/`urllib`).
- Direcção: o domínio **não** conhece a API; a Application consome os
  contratos, nunca internos.

## Interfaces

```python
ApiRequest(method, path, headers={}, body="")     # imutável
ApiResponse(status, payload={}, headers={})       # imutável
ApiGateway.handle(request) -> ApiResponse         # porte injectável
StdLibHttpGateway() .serve(host, port) .shutdown()
health(ApiRequest) -> ApiResponse                 # GET /health
API_CONTRACT_VERSION == "1.0"                     # fora de __all__
```

## Decisões

1. **Contract-first, transporte injectável** — o `ApiGateway` isola os
   handlers do transporte; trocar HTTP por ASGI/outro é criar um adapter,
   sem tocar nos contratos (padrão de adaptadores do Provider).
2. **Stdlib no primeiro transporte** — zero dependências novas; coerente
   com "sem dependências pesadas" do núcleo e com a política do projecto.
3. **Exemplo sem domínio** — `/health` só reporta versões; os recursos de
   domínio entram por unidades API-02+ com as suas arestas justificadas.

## Validação

```text
py -3.12 -m pytest
tests=512  failures=0  errors=0  skipped=0
```

(506 bases + 6 novos: 1 versão de superfície + 5 do gateway.)