---
description: Validar módulos, integrações e a fundação do WSAI 2 através de um gate formal e não destrutivo
agent: plan
---
# /wsai-validate — FOUNDATION VALIDATION GATE

## Missão

Executar uma validação estruturada do estado real do WorkStation AI 2 sem introduzir alterações funcionais automáticas.

Este comando é um mecanismo de qualidade e governação. Determina se um módulo, uma integração ou a fundação completa está suficientemente sólida para ser aprovada.

## Modos suportados

```text
/wsai-validate module <nome>
/wsai-validate integration
/wsai-validate foundation
/wsai-validate full
```

## Regra fundamental

VALIDAR NÃO É IMPLEMENTAR.

Durante a validação não criar, apagar, mover ou refactorizar código funcional apenas para fazer a validação passar. Problemas encontrados devem ser classificados e encaminhados para o ciclo controlado.

## Pré-flight obrigatório

1. Ler `AGENTS.md`.
2. Ler `docs/project/PROJECT_STATE.md`.
3. Ler `docs/project/ROADMAP.md`.
4. Ler arquitectura e constituição aplicáveis.
5. Inspeccionar a árvore real.
6. Verificar Git sem o modificar.
7. Inventariar módulos, testes, documentação e dependências relevantes.
8. Identificar alterações locais que possam afectar a validade do resultado.

## Áreas de validação

### 1. Inventário e estado real

Distinguir IMPLEMENTADO, PARCIAL, AUSENTE e NÃO APLICÁVEL. Não considerar documentação como prova de implementação.

### 2. Arquitectura

Verificar fronteiras, dependências, imports proibidos, ciclos, duplicações, acoplamento, ownership e contratos arquitecturais.

### 3. Código e contratos

Analisar responsabilidades, interfaces públicas, tipos/dados, erros, lifecycle, timeout, cancellation, cleanup, estado mutável, código morto/duplicado e integrações.

### 4. Testes

Executar e analisar, quando aplicável, testes unitários, integração, negativos, segurança, regressão e contratos arquitecturais. Assinalar testes frágeis que passem sem observar o comportamento que afirmam validar.

### 5. Integração e recuperação

Validar dependências indisponíveis, incompatibilidades, recursos insuficientes, timeout, cancelamento, falha controlada, libertação de recursos, recuperação e consistência do estado.

### 6. Documentação ↔ Código ↔ Testes

Comparar as três fontes e procurar funcionalidades documentadas mas inexistentes, código sem documentação necessária, testes desalinhados, estados contraditórios e comandos desactualizados.

## Classificação de problemas

```text
P0 — Crítico: risco de corrupção, segurança, perda de dados ou violação grave do Core.
P1 — Alto: comportamento incorrecto, contrato quebrado ou integração crítica incompleta.
P2 — Médio: fragilidade, inconsistência ou lacuna que deve ser resolvida antes da aprovação final.
P3 — Baixo: melhoria de qualidade ou optimização sem impacto imediato.
```

## Critérios de decisão

### 🟢 APPROVED

Sem P0/P1/P2 bloqueantes e com evidência suficiente.

### 🟡 APPROVED WITH WARNINGS

Sem P0/P1/P2; apenas P3 documentados.

### 🔴 NOT APPROVED

Existe bloqueio P0/P1/P2 ou não foi possível demonstrar adequadamente a conformidade.

## Foundation Validation Gate

`/wsai-validate foundation` só pode declarar `FOUNDATION APPROVED` quando todos os núcleos definidos como fundamentais no estado e arquitectura aplicáveis estiverem concluídos e a evidência for suficiente.

A aprovação é um **estado formal de governação**, não um pedido de confirmação humana. Quando executado dentro de `/wsai-run`, o orquestrador deve consumir automaticamente esse estado, actualizar `PROJECT_STATE.md` e determinar a próxima unidade através de `ROADMAP.md`.

Se houver apenas um P2 documental/processual inequívoco, localizado e sem impacto funcional/arquitectural, o resultado deve continuar a ser `NOT APPROVED`, mas o bloqueio pode ser tratado pelo `/wsai-run` como unidade correctiva autónoma, seguindo `PLAN → IMPLEMENT → TEST → VALIDATE`. Não deve ser considerado motivo para solicitar uma aprovação humana intermédia.

## Relatório obrigatório

Toda a execução deve produzir um relatório claro no fluxo e, quando a configuração permitir, actualizar ou criar:

```text
docs/validation/FOUNDATION_VALIDATION_REPORT.md
```

O relatório deve incluir:

```text
WSAI 2 — FOUNDATION VALIDATION REPORT

Data:
Commit:
Branch:
Modo:
Alvo:

1. RESULTADO GLOBAL
2. INVENTÁRIO
3. ARQUITECTURA
4. CÓDIGO E CONTRATOS
5. TESTES
6. INTEGRAÇÕES E RECUPERAÇÃO
7. DOCUMENTAÇÃO
8. PROBLEMAS DETECTADOS
9. DECISÃO FINAL
10. PRÓXIMO COMANDO RECOMENDADO
```

Cada problema deve indicar, sempre que possível: ID, Prioridade, Módulo/ficheiro, Descrição, Evidência, Impacto, Dependências afectadas e Recomendação.

## Próximo passo obrigatório

Se existirem bloqueios:

```text
RESULTADO: NOT APPROVED
PRÓXIMO COMANDO RECOMENDADO: /wsai-plan
```

Quando executado isoladamente, isto é orientação para o utilizador. Quando executado como etapa interna de `/wsai-run`, é uma transição interna do ciclo e **não constitui, por si só, uma paragem nem um pedido de confirmação**. O `/wsai-run` deve classificar o bloqueio e, se estiver dentro das regras de correcção autónoma, continuar o ciclo.

Se aprovado:

```text
RESULTADO: APPROVED
PRÓXIMO PASSO: determinado automaticamente a partir de PROJECT_STATE.md e ROADMAP.md.
```

## Protecções

- Não declarar aprovação apenas porque todos os testes passaram.
- Não alterar código funcional durante a validação.
- Não iniciar API, UI ou addons apenas por intenção futura.
- Não considerar uma fase concluída sem evidência no código, testes e estado persistente.
- Não parar por um P2 documental/processual inequívoco quando `/wsai-run` o puder corrigir autonomamente.
- Parar e marcar `NOT APPROVED` quando existir decisão arquitectural material ainda não definida.
