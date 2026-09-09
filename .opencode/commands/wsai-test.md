---
description: Validar uma alteração ou unidade WSAI 2 e tratar regressões
agent: build
---
# /wsai-test — VALIDAÇÃO CONTROLADA

Validar `$ARGUMENTS` ou, se vazio, a unidade actualmente trabalhada.

## Contrato de transição

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`.

Para alterações estruturais, testar também a integridade das fronteiras e a ausência de consumidores esquecidos. Uma migração não está segura apenas porque os testes funcionais imediatos passam.

## Sequência

1. Identificar testes afectados.
2. Executar testes focados.
3. Executar integração relevante.
4. Para alteração estrutural, executar testes arquitecturais/dependências quando disponíveis.
5. Executar suíte completa antes do fecho quando o impacto o justificar.
6. Comparar com baseline.
7. Corrigir falhas relacionadas quando seguro e repetir.

## Regressão crítica

Para comandos, contratos, Kernel, Runtime ou governação verificar:

- execução autónoma;
- continuidade;
- progresso visível;
- estado persistente;
- Dependency Firewall;
- imports/ciclos proibidos;
- não regressão dos subsistemas concluídos.

## Resultado

```text
WSAI 2 — VALIDAÇÃO
Alvo: ...
Arquitectura: LEGACY | TRANSITION | TARGET | FROZEN
Tipo alteração: ...
Testes focados: ...
Integração: ...
Arquitecturais: ...
Suíte: ...
Baseline: ...
Falhas: ...
Correcções: ...
Estado: APROVADO | BLOQUEADO
```

Nunca transformar falha em sucesso omitindo testes ou alterando artificialmente a baseline.
