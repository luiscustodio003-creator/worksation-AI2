# WSAI 2 — Validation Reports

## Objectivo

Este directório contém os relatórios persistentes produzidos pelos processos formais de validação do WorkStation AI 2.

A validação é complementar ao ciclo normal de desenvolvimento:

```text
AUDITAR → PLANEAR → IMPLEMENTAR → TESTAR → DOCUMENTAR → SINCRONIZAR
```

O gate de validação verifica, sobre o estado real do repositório, se existe evidência suficiente para aprovar um módulo, integração ou fundação.

## Comando oficial

```text
/wsai-validate module <nome>
/wsai-validate integration
/wsai-validate foundation
/wsai-validate full
```

## Relatório principal

O relatório consolidado da fundação utiliza o caminho:

```text
docs/validation/FOUNDATION_VALIDATION_REPORT.md
```

O relatório deve ser actualizado apenas quando existir uma execução formal de validação com evidência suficiente. Não deve conter resultados inventados nem declarar aprovação antecipada.

## Regra de aprovação

`FOUNDATION APPROVED` não significa apenas que os testes existentes passaram. A aprovação exige análise aplicável de:

- arquitectura;
- contratos;
- código;
- testes;
- integração e recuperação;
- documentação;
- estado persistente.

Se forem detectados problemas bloqueantes, a validação encaminha o trabalho para o ciclo controlado de correcção e posterior revalidação.
