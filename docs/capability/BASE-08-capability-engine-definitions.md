# WORKSTATION AI 2 — RELATÓRIO DA BASE: CAPABILITY ENGINE (DEFINIÇÕES E REGISTO)

## O que foi feito

Iniciou-se a **Fase 4 — Capability Engine** (subsistema 3.4) com as
**definições de capacidade** e o **registo** central. A capacidade é a
entidade declarativa que o sistema pode disponibilizar (ex.: inferência
local de modelos, embeddings) com requisitos mínimos quantificados.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.4 Capability Engine** descrito em
`docs/architecture/ARCHITECTURE.md`: "Determina as capacidades reais que
o sistema consegue disponibilizar a partir de hardware, runtime, software
e fornecedores instalados." Esta unidade cobre a parte de *definições* e
*registo*; a avaliação contra hardware/runtime pertence às unidades
seguintes.

## Para que serve

- Define o contrato de capacidade com `CapabilityDefinition` e requisitos
  quantificados `CapabilityRequirements`.
- Mantém o catálogo central via `CapabilityRegistry`
  (registar/obter/remover/listar).
- Fornece um catálogo base (`default_capabilities()` /
  `create_default_registry()`) para as unidades seguintes avaliarem.

## Ficheiros criados

- `src/wsai2/capability/base.py` — `CapabilityDefinition`,
  `CapabilityRequirements`
- `src/wsai2/capability/registry.py` — `CapabilityRegistry`,
  `default_capabilities()`, `create_default_registry()`
- `src/wsai2/capability/__init__.py` — interface pública
- `tests/test_capability.py` — validação
- `docs/capability/BASE-08-capability-engine-definitions.md`

## Dependências

Nenhuma para além da biblioteca padrão. O subsistema é de domínio puro:
os perfis de hardware e runtime são consumidos apenas pela avaliação
(unidades futuras), respeitando as fronteiras da arquitectura.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **60 testes aprovados** (3 fundação + 5 platform + 17 hardware
+ 24 runtime + 11 capability).

Os testes validam:

- Requisitos por defeito e com GPU obrigatória (`has_gpu_requirement`);
- Estrutura e resumo textual de `CapabilityDefinition`;
- Catálogo base não vazio e com ids únicos;
- Registo por defeito pré-carregado;
- Registo, substituição por id, remoção e listagem.

## Estado da fase

**Fase 4 — Capability Engine** — **EM PROGRESSO**.

Itens do roadmap implementados nesta unidade:

- definições de capacidade ✓ (`CapabilityDefinition`, `CapabilityRequirements`)
- registo ✓ (`CapabilityRegistry`, catálogo base)

Itens pendentes:

- avaliação;
- compatibilidade;
- capacidades disponíveis.

## Próximo passo

Unidade seguinte da Fase 4: avaliação de capacidades contra o perfil de
hardware e o estado de runtime (veredictos `disponível`/`indisponível`
com justificação), preparando a compatibilidade e a lista de capacidades
disponíveis.