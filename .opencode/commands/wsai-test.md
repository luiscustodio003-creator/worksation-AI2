---
description: Validar uma alteração ou unidade WSAI 2 e tratar regressões
agent: build
---
# /wsai-test — VALIDAÇÃO CONTROLADA

Validar `$ARGUMENTS` ou, se vazio, a unidade actualmente trabalhada.

## Sequência

1. Identificar os testes directamente afectados.
2. Executar primeiro testes focados.
3. Executar testes de integração relevantes.
4. Executar a suíte completa quando a alteração for estrutural ou antes da conclusão.
5. Comparar resultados com a baseline conhecida.
6. Se houver falhas relacionadas com a alteração e a correcção for segura, corrigir e repetir.
7. Se a falha não estiver relacionada ou não puder ser resolvida com segurança, não mascarar o resultado: reportar e parar a unidade.

## Regressão crítica

Para alterações no `wsai-run`, comandos OpenCode, contratos, Runtime Engine ou governação, verificar adicionalmente:

- execução autónoma;
- selecção da próxima unidade;
- continuidade entre etapas;
- visibilidade do progresso;
- actualização de estado;
- não regressão dos subsistemas já concluídos.

## Resultado

```text
WSAI 2 — VALIDAÇÃO
Alvo: ...
Testes focados: ...
Integração: ...
Suíte completa: ...
Baseline: ...
Falhas: ...
Correcções: ...
Estado: APROVADO | BLOQUEADO
```

Nunca transformar uma falha em sucesso omitindo testes ou alterando artificialmente a baseline.
