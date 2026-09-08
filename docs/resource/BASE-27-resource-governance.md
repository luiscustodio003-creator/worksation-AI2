# WORKSTATION AI 2 — RELATÓRIO DA BASE: RESOURCE GOVERNANCE

## O que foi feito

Foi criada a **governação de recursos** da Fase 8 (hardening 05 do
CORE_HARDENING_PLAN) num novo subsistema **`wsai2.resource`**:
normalização de limites declarativos (`ResourceLimit`), validação de
folga efectiva contra os perfis existentes de hardware e runtime e
contabilidade de alocações/reservas (accounting) ao longo de execuções.
Unidade **Fase 8.3**.

A governação **evolui a gestão de memória existente sem duplicar
mecanismos**: a medição estrutural continua no subsistema
`wsai2.hardware` (Hardware Capability) e a medição momentânea no
`wsai2.runtime` (Runtime State). Não foi implementado enforce de tempo
(8.4) nem scheduling/gestor de execução (8.5).

## Onde se encaixa na arquitectura

- **Fase 8 — Runtime Engine** (subsistema 3.8), etapa 8.3 do
  CORE_HARDENING_PLAN (hardening 05).
- `wsai2.resource` é um subsistema **folha** que consome contratos dos
  subsistemas já concluídos (hardware, runtime e a taxonomia de erros do
  `wsai2.core`), sem depender de nenhum motor de execução.
- O `Runtime Manager` (8.5) consumirá o governador para reservar e
  validar recursos quando iniciar execuções; o `ExecutionContext.budget`
  (8.2) é o orçamento declarativo que o governador sabe avaliar.

## Para que serve

- **Normalizar** limites declarativos por dimensão conhecida (RAM, CPU,
  VRAM, disco), com conversão de unidade (`memory_mb` vs `ram_gb`, etc.).
- **Validar** a folga efectiva: `required <= min(capacity − committed,
  available_now − committed)` — capacidade estrutural **e** disponibilidade
  momentânea, descontando o já reservado.
- **Contabilizar** alocações (`allocate` / `release`), mantendo por
  instância o livro de reservas (`outstanding`, `committed_for`) sem
  estado global.
- **Reportar de forma explícita** dimensões não reconhecidas
  (`ResourceVerdict.UNRECOGNIZED`) em vez de passar silenciosamente.

## Ficheiros criados/alterados

- `src/wsai2/resource/base.py` — contratos: `ResourceDimension`,
  `ResourceVerdict`, `AllocationState`, `ResourceCheck`,
  `ResourceBudgetResult`, `ResourceAllocation` (declarativos, sem lógica)
- `src/wsai2/resource/governor.py` — `ResourceGovernor` (normalização,
  validação, accounting; usa `ResourceError` de `wsai2.core`)
- `src/wsai2/resource/__init__.py` — exports públicos do submódulo
- `tests/test_resource_governor.py` — 21 testes
- `docs/resource/BASE-27-resource-governance.md` — este relatório

Nenhum módulo existente das Fases 1–7 ou da 8.1/8.2 foi alterado.

## Dependências

- `base.py`: apenas stdlib (`dataclasses`, `enum`).
- `governor.py`: `wsai2.hardware` (`HardwareProfile`), `wsai2.runtime`
  (`RuntimeProfile`), `wsai2.core.errors` (`ResourceError`). A referência
  a `ResourceLimit` (`wsai2.extension`, 8.1) é **apenas tipográfica**
  (`TYPE_CHECKING`), seguindo o padrão do núcleo folha.
- Direcção das dependências: `resource` aponta para dentro (hardware,
  runtime, core, extension) — não é consumido por ninguém fora do Runtime
  Engine. **Não duplica** a lógica de `capability/evaluation.py` nem de
  `model/compatibility.py` (esses avaliam requisitos de capacidade/modelo;
  o governador avalia limites declarativos com accounting).

## Decisões arquitecturais registadas

1. **Subsistema folha dedicado** (`wsai2.resource`), cliente dos perfis
   existentes: a medição não é reescrita nem duplicada; `resource` cruza
   e contabiliza. Distingue-se de `runtime` (que mede) e de `core` (que
   transporta o contexto e o orçamento).
2. **Mapa fechado de dimensões** com `UNRECOGNIZED` explícito: nomes
   fora do mapa (`ram`, `memory_mb`, `cpu`, `cpu_cores`, `vram*`,
   `disk*`, `storage*`) não falham nem passam em silêncio — produzem
   veredicto de dimensão desconhecida no resultado.
3. **Hardware Capability ≠ Runtime State mantido:** `capacity` vem do
   `HardwareProfile` (estrutural); `available_now` vem do `RuntimeProfile`
   (momentâneo). Em `cpu`, a folga é derivada da carga global
   (`count × (100 − percent)%`), sem nova leitura.
4. **Limitação documentada:** sem leituras de runtime para VRAM em uso e
   espaço livre de disco nesta unidade — essas dimensões são governadas
   pela capacidade estrutural (`available_now = None`). A ampliação para
   leituras efectivas fica como evolução futura se a governação o exigir.
5. **Accounting por instância, sem estado global:** cada `ResourceGovernor`
   tem o seu livro de alocações; `release` é idempotente; alocações
   duplicadas e `release` desconhecido falham com `ResourceError`
   (`wsai.resource.insufficient|duplicate|unknown`).
6. **Reutilização da taxonomia 8.2:** as falhas de governação usam
   `ResourceError`, coeso com o modelo transversal; o orçamento é o
   `tuple[ResourceLimit, ...]` já aceite pelo `ExecutionContext`.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **264 testes aprovados** (21 resource + 22 core + 12 extension
+ 39 task + 46 provider + 42 model + 33 capability + 24 runtime + 17
hardware + 5 platform + 3 fundação). Regressão dos 243 anteriores
intacta — alteração 100% aditiva.

Os 21 testes validam:

- orçamento vazio satisfeito por vacuidade;
- normalização `memory_mb` → GB e conversão de unidades;
- veredictos por dimensão (RAM, CPU, VRAM, disco): satisfeito /
  insatisfeito em função da capacidade estrutural e da folga momentânea;
- carga de CPU alta reduz os núcleos livres efectivos;
- dimensão não reconhecida → `UNRECOGNIZED` (explícita);
- VRAM/disco sem leitura runtime → governados pela capacidade estrutural;
- limite negativo sem pretensão (valor nulo);
- accounting: reserva contabilizada, sobre-compromisso rejeitado,
  libertação devolve recursos, `release` de alocação desconhecida falha,
  `release` idempotente, id explícito não duplicável.

## Estado da fase

**Fase 8 — Runtime Engine — EM CURSO**.

Etapas concluídas:

- 8.0 baseline e auditoria ✓
- 8.1 contratos mínimos — Extension Contract ✓
- 8.2 Execution Context + Error Model ✓
- 8.3 Resource Governance ✓ (esta unidade)

Em falta (unidades posteriores): timeout/cancellation/recovery (8.4),
Runtime Manager + scheduler (8.5), lifecycle + compatibilidade (8.6),
testes de contrato arquitectural (8.7).

## Riscos residuais

- **Dimensões não mapeadas** produzem `UNRECOGNIZED`; novas dimensões
  exigem adição ao mapa de normalização em `governor.py`.
- **`cpu` governa núcleos**, não percentagem de CPU; cotas percentuais
  (se necessárias em 8.4) implicam extensão do governador.
- **VRAM e disco** são governados pela capacidade estrutural (sem leitura
  de runtime); a monitorização fina fica para evolução futura.
- O orçamento do `ExecutionContext.budget` é **ainda declarativo**: só se
  torna uma reserva real quando o gestor de execução (8.5) chamar o
  governador.

## Próximo passo

Fase 8.4 — **Timeout + Cancellation + Recovery**: centralizar no Runtime
Engine as políticas de limite temporal, cancelamento efectivo e
recuperação sobre o `ExecutionContext` e o modelo de erros já existentes.