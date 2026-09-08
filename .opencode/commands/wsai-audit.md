---
description: Auditar o estado real antes de alterar o WorkStation AI 2
agent: plan
---
# /wsai-audit — AUDITORIA CONTROLADA

Executar uma auditoria **sem alterar código funcional**.

## Objectivo

Determinar o estado real da área `$ARGUMENTS` ou, se vazio, da base necessária para a próxima unidade do projecto.

## Procedimento obrigatório

1. Ler `AGENTS.md`.
2. Ler `docs/project/PROJECT_STATE.md` e `docs/project/ROADMAP.md`.
3. Ler a arquitectura e a constituição relevantes.
4. Inspeccionar a árvore e os módulos existentes.
5. Procurar responsabilidades já implementadas antes de propor ficheiros novos.
6. Verificar testes existentes e documentação associada.
7. Verificar o estado Git sem o modificar.
8. Mapear dependências e pontos de integração.
9. Classificar cada requisito como:
   - IMPLEMENTADO;
   - PARCIAL;
   - INTEGRAÇÃO NECESSÁRIA;
   - AUSENTE;
   - NÃO NECESSÁRIO.

## Regra de segurança

Não criar, apagar, mover ou refactorizar código funcional durante esta auditoria, excepto se for estritamente necessário para obter informação e não alterar o comportamento.

## Resultado obrigatório

Produzir:

```text
WSAI 2 — AUDITORIA
Área: ...
Estado actual: ...
Já existe: ...
Parcial: ...
Em falta: ...
Duplicações/riscos: ...
Dependências: ...
Testes existentes: ...
Ficheiros afectados (potenciais): ...
Risco: BAIXO | MÉDIO | ALTO
Recomendação: ...
```

A auditoria é uma fotografia do estado real. Não inventar componentes futuros como se já existissem.
