---
description: Rever e sincronizar Git de uma unidade WSAI 2 com segurança
agent: build
---
# /wsai-git — SINCRONIZAÇÃO CONTROLADA

Rever e sincronizar a unidade `$ARGUMENTS` ou a alteração actual.

## Protecção da migração

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`.

Antes de commit/push verificar se a alteração estrutural pertence a uma unidade coerente e se não existem consumidores ou ficheiros não relacionados. Em `TRANSITION`, confirmar também que a origem não foi eliminada prematuramente.

## Pré-condições

```text
git status
git branch --show-current
git remote -v
git diff --stat
git diff
```

Actualizar referências remotas sem sobrescrever alterações locais.

## Checklist

1. Unidade coerente?
2. Tipo de alteração identificado?
3. Ficheiros não relacionados?
4. Testes aplicáveis passaram?
5. Arquitectura/contratos validados?
6. Documentação e estado actualizados?
7. Consumidores/dependências verificados?
8. Divergência remota?
9. Commit reversível e descritivo?

## Segurança

- Nunca reset destrutivo.
- Nunca force push como solução normal.
- Nunca apagar trabalho local desconhecido.
- Parar perante conflito inseguro.

## Commit

Criar commit apenas após validação e coerência da unidade. Push apenas quando permitido e seguro. Verificar estado final.

## Resultado

```text
WSAI 2 — GIT
Branch: ...
Unidade: ...
Tipo alteração: ...
Ficheiros: ...
Testes: ...
Validação: ...
Commit: ...
Push: ...
Estado final: ...
```
