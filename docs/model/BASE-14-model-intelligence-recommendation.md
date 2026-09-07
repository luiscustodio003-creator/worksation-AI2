# WORKSTATION AI 2 — RELATÓRIO DA BASE: MODEL INTELLIGENCE (RECOMENDAÇÃO)

## O que foi feito

Foi implementada a **recomendação de modelos**, a unidade que **encerra a
Fase 5 — Model Intelligence**: dado o estado real do sistema (hardware,
runtime e capacidades) e, opcionalmente, uma categoria funcional
pretendida, o sistema recomenda o modelo **mais adequado** do registo,
com justificação textual e alternativas ordenadas.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.5 Model Intelligence** ("adequação às
tarefas"), item **recomendação** do roadmap da Fase 5. Assenta na
classificação (categoria + score) e na compatibilidade das unidades
anteriores. Com ela, os seis itens do roadmap da fase estão
implementados: registo, metadados, requisitos, compatibilidade,
classificação e recomendação.

## Para que serve

- Recomenda o melhor modelo disponível para uma categoria pretendida
  (chat / completion / embeddings) ou para o sistema em geral.
- Exclui modelos **indisponíveis** e justifica a escolha em linguagem
  natural.
- Devolve alternativas ordenadas, preparando a decisão e a exposição na
  API/UI.

## Política de recomendação (documentada e determinística)

1. **Candidatos** — modelos com score de adequação > 0 que correspondam
   à categoria pedida (ou todos, quando não há categoria). Modelos
   indisponíveis (score 0.0) nunca são recomendados.
2. **Ordenação** — score de adequação decrescente; em empate, mais
   parâmetros (mais capaz); depois menor exigência de RAM; e, por fim,
   id para estabilidade.
3. **Resultado** — o melhor candidato com estado, categoria, razão e as
   alternativas (no máximo três). Sem candidatos → `None`.

Esta política é intencionalmente simples e reversível; refinamentos por
critérios de tarefa pertencem à Task Intelligence (Fase 7).

## Ficheiros criados/alterados

- `src/wsai2/model/recommendation.py` — **novo**: `ModelRecommendation`,
  `recommend_model`
- `src/wsai2/model/__init__.py` — exporta novos tipos e função
- `tests/test_model_recommendation.py` — **novo**
- `docs/model/BASE-14-model-intelligence-recommendation.md`

## Dependências

- `wsai2.model.classification` (score, categoria)
- `wsai2.model.compatibility` (veredictos)
- `wsai2.capability`, `wsai2.hardware`, `wsai2.runtime` (entradas)
- Sem dependências novas de terceiros.

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **124 testes aprovados** (10 recomendação + 32 model + 33
capability + 3 fundação + 5 platform + 17 hardware + 24 runtime).

Os testes validam:

- vencedor por parâmetros quando tudo disponível;
- filtragem por categoria, reflexo de score/estado e `is_suitable`;
- alternativas sem repetir o escolhido;
- categorias sem candidatos → `None`; registo vazio → `None`;
- exclusão de modelo indisponível mesmo com mais parâmetros;
- justificação de disponível e de condicionado.

## Estado da fase

**Fase 5 — Model Intelligence — CONCLUÍDA (100%)**.

Itens do roadmap implementados:

- registo de modelos ✓
- metadados ✓
- requisitos ✓
- compatibilidade ✓
- classificação ✓
- recomendação ✓

## Próximo passo

Iniciar a **Fase 6 — Provider Layer** (subsistema 3.6): contratos de
fornecedor, detecção, adaptadores de runtime e health checks. Novo
subsistema com decisão estrutural própria — a iniciar em execução
seguinte.