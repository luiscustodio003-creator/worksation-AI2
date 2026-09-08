---
description: Validar módulos, integrações e a fundação do WSAI 2 através de um gate formal e não destrutivo
agent: plan
---
# /wsai-validate — FOUNDATION VALIDATION GATE

## Missão

Executar uma validação estruturada do estado real do WorkStation AI 2 sem introduzir alterações funcionais automáticas.

Este comando é um mecanismo de qualidade e governação. O seu objectivo é determinar se um módulo, uma integração ou a fundação completa está suficientemente sólida para ser aprovada.

## Modos suportados

```text
/wsai-validate module <nome>
/wsai-validate integration
/wsai-validate foundation
/wsai-validate full
```

Se o argumento estiver vazio, determinar o modo mais seguro a partir de `PROJECT_STATE.md`, sem assumir que a fundação está pronta para validação final.

## Regra fundamental

VALIDAR NÃO É IMPLEMENTAR.

Durante a validação não criar, apagar, mover ou refactorizar código funcional apenas para fazer a validação passar. Problemas encontrados devem ser classificados, documentados e encaminhados para o ciclo controlado:

```text
/wsai-audit
      ↓
/wsai-plan
      ↓
/wsai-implement
      ↓
/wsai-test
      ↓
/wsai-validate
```

## Pré-flight obrigatório

1. Ler `AGENTS.md`.
2. Ler `docs/project/PROJECT_STATE.md`.
3. Ler `docs/project/ROADMAP.md`.
4. Ler a arquitectura e constituição aplicáveis ao alvo.
5. Inspeccionar a árvore real do projecto.
6. Verificar o estado Git sem o modificar.
7. Inventariar módulos, testes, documentação e dependências relevantes.
8. Identificar alterações locais que possam afectar a validade do resultado.

## Áreas de validação

### 1. Inventário e estado real

Verificar o que existe efectivamente no repositório e distinguir:

- IMPLEMENTADO;
- PARCIAL;
- AUSENTE;
- NÃO APLICÁVEL.

Não considerar documentação como prova de implementação.

### 2. Arquitectura

Verificar:

- fronteiras entre camadas;
- direcção das dependências;
- imports proibidos;
- dependências circulares;
- responsabilidades duplicadas;
- acoplamento excessivo;
- módulos órfãos ou responsabilidades sem proprietário claro;
- conformidade com os contratos arquitecturais existentes.

### 3. Código e contratos

Analisar, proporcionalmente ao alvo:

- responsabilidade principal;
- interfaces públicas;
- coerência de tipos e dados;
- tratamento de erros;
- ownership e lifecycle;
- timeout;
- cancellation;
- cleanup;
- estado mutável;
- código morto ou duplicado;
- pontos de integração.

### 4. Testes

Executar e analisar, quando aplicável:

- testes unitários;
- testes de integração;
- testes negativos;
- testes de segurança;
- testes de regressão;
- testes de contratos arquitecturais;
- gates existentes.

Não usar apenas o número de testes como indicador de qualidade. Assinalar testes potencialmente frágeis quando passam sem observar o comportamento que afirmam validar.

### 5. Integração e recuperação

Validar cenários relevantes de:

- dependência indisponível;
- incompatibilidade;
- recursos insuficientes;
- timeout;
- cancelamento;
- falha controlada;
- libertação de recursos;
- recuperação e consistência do estado.

### 6. Documentação ↔ Código ↔ Testes

Comparar as três fontes e procurar:

- funcionalidades documentadas mas inexistentes;
- código implementado sem documentação necessária;
- testes que não correspondem ao contrato;
- estados de fase contraditórios;
- comandos e procedimentos desactualizados.

## Classificação de problemas

```text
P0 — Crítico: risco de corrupção, segurança, perda de dados ou violação grave do Core.
P1 — Alto: comportamento incorrecto, contrato quebrado ou integração crítica incompleta.
P2 — Médio: fragilidade, inconsistência ou lacuna que deve ser resolvida antes da aprovação final.
P3 — Baixo: melhoria de qualidade ou optimização sem impacto imediato na integridade.
```

## Critérios de decisão

### 🟢 APPROVED

O alvo cumpre os critérios aplicáveis e não existem problemas P0, P1 ou P2 que bloqueiem a aprovação.

### 🟡 APPROVED WITH WARNINGS

O alvo está funcional e coerente, mas existem avisos P3 documentados que não comprometem a progressão aprovada.

### 🔴 NOT APPROVED

Existe pelo menos um problema bloqueante ou não foi possível demonstrar adequadamente a conformidade do alvo.

## Foundation Validation Gate

O modo:

```text
/wsai-validate foundation
```

só pode declarar `FOUNDATION APPROVED` quando todos os núcleos definidos como fundamentais no estado e arquitectura aplicáveis estiverem concluídos e a evidência de validação for suficiente.

A aprovação da fundação é um gate formal antes de iniciar camadas que dependam da sua estabilidade, conforme a decisão registada no planeamento do projecto.

## Relatório obrigatório

Toda a execução deve produzir um relatório claro no fluxo de execução e, quando a configuração do projecto permitir, actualizar ou criar o relatório persistente em:

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

Cada problema deve indicar, sempre que possível:

```text
ID:
Prioridade:
Módulo/ficheiro:
Descrição:
Evidência:
Impacto:
Dependências afectadas:
Recomendação:
```

## Próximo passo obrigatório

A validação deve terminar sempre com orientação accionável.

Se existirem problemas bloqueantes:

```text
RESULTADO: NOT APPROVED
PRÓXIMO COMANDO RECOMENDADO: /wsai-plan
OBJECTIVO: planear a correcção dos problemas identificados sem alterar o código durante a análise.
```

Depois do planeamento:

```text
/wsai-implement
/wsai-test
/wsai-validate <mesmo alvo>
```

Se o alvo for aprovado:

```text
RESULTADO: APPROVED
PRÓXIMO PASSO: determinado a partir de PROJECT_STATE.md e ROADMAP.md.
```

## Protecções

- Não declarar aprovação apenas porque todos os testes passaram.
- Não alterar código funcional para esconder uma falha.
- Não iniciar API, UI ou addons apenas porque existe uma intenção futura.
- Não considerar uma fase concluída sem evidência no código, testes e estado persistente.
- Não substituir a auditoria normal; a validação utiliza os seus resultados como evidência complementar.
- Parar e marcar `NOT APPROVED` quando existir uma decisão arquitectural material ainda não definida.
