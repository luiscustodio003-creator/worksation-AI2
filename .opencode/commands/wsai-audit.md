---
description: Auditar o estado real antes de alterar o WorkStation AI 2
agent: plan
---
# /wsai-audit — AUDITORIA CONTROLADA

Executar uma auditoria **sem alterar código funcional**.

## Objectivo

Determinar o estado real da área `$ARGUMENTS` ou, se vazio, da base necessária para a próxima unidade do projecto.

A auditoria deve cruzar **código, testes, documentação e Git**. A documentação pode declarar intenção ou estado, mas não é prova suficiente de implementação.

## Procedimento obrigatório

1. Ler `AGENTS.md`.
2. Ler `docs/project/PROJECT_STATE.md` e `docs/project/ROADMAP.md`.
3. Ler a arquitectura e a constituição relevantes.
4. Inspeccionar a árvore e os módulos existentes.
5. Procurar responsabilidades já implementadas antes de propor ficheiros novos.
6. Verificar testes existentes e documentação associada.
7. Verificar o estado Git sem o modificar.
8. Mapear dependências e pontos de integração.
9. Comparar código ↔ testes ↔ documentação.
10. Procurar testes que passem sem exercer o comportamento que afirmam validar.
11. Classificar cada requisito como:
   - IMPLEMENTADO;
   - PARCIAL;
   - INTEGRAÇÃO NECESSÁRIA;
   - AUSENTE;
   - NÃO NECESSÁRIO.

## Regra de segurança

Não criar, apagar, mover ou refactorizar código funcional durante esta auditoria, excepto se for estritamente necessário para obter informação e não alterar o comportamento.

Se for encontrada uma falha, registá-la com prioridade e encaminhá-la para `/wsai-plan`; não alterar o código apenas para obter uma auditoria verde.

## Resultado obrigatório

Produzir:

```text
WSAI 2 — AUDITORIA
Área: ...
Commit: ...
Estado actual: ...
Já existe: ...
Parcial: ...
Em falta: ...
Duplicações/riscos: ...
Dependências: ...
Testes existentes: ...
Qualidade dos testes: ...
Documentação consistente: SIM | NÃO | PARCIAL
Ficheiros afectados (potenciais): ...
Problemas: P0 | P1 | P2 | P3
Risco: BAIXO | MÉDIO | ALTO
Recomendação: ...
```

Para auditorias de fundação ou marcos relevantes, actualizar o relatório persistente definido pelo projecto, nomeadamente `docs/validation/FOUNDATION_READINESS_AUDIT.md` quando esse artefacto for o relatório em vigor.

## Relação com os restantes comandos

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
      ↓
/wsai-doc
      ↓
/wsai-git
```

`/wsai-run` compõe este ciclo autonomamente. Não deve ignorar uma lacuna material encontrada pela auditoria.

## Regra de decisão

Se uma responsabilidade já existir, evoluí-la ou integrá-la em vez de criar uma implementação paralela.

Se existir uma decisão arquitectural material ainda não definida, marcar a auditoria como bloqueada e não inventar a decisão.

A auditoria é uma fotografia do estado real. Não inventar componentes futuros como se já existissem.
