---
description: Rever e sincronizar Git de uma unidade WSAI 2 com segurança
agent: build
---
# /wsai-git — SINCRONIZAÇÃO CONTROLADA

Rever e sincronizar a unidade `$ARGUMENTS` ou a alteração actual.

## Pré-condições

Não fazer commit/push de alterações cujo objectivo não esteja claro.

Verificar:

```text
git status
git branch --show-current
git remote -v
git diff --stat
git diff
```

Quando permitido pelo ambiente, actualizar referências remotas sem sobrescrever alterações locais.

## Checklist

1. A alteração pertence a uma única unidade coerente?
2. Há ficheiros não relacionados?
3. Os testes aplicáveis passaram?
4. A documentação e o estado foram actualizados?
5. Existem alterações locais que não pertencem a esta unidade?
6. Existe divergência remota?
7. O commit é reversível e descritivo?

## Segurança

- Nunca fazer reset destrutivo.
- Nunca fazer force push como solução normal.
- Nunca apagar trabalho local desconhecido.
- Se houver conflito Git inseguro, parar e reportar.

## Commit

Criar um commit apenas quando a unidade estiver validada e coerente.

Depois do commit, verificar novamente o estado. Fazer push apenas quando autorizado pelo ambiente e sem conflito.

## Resultado

```text
WSAI 2 — GIT
Branch: ...
Ficheiros: ...
Testes: ...
Commit: ...
Push: ...
Estado final: ...
```
