---
description: Planear uma unidade WSAI 2 sem iniciar a implementação
agent: plan
---
# /wsai-plan — PLANEAMENTO CONTROLADO

Planear a unidade `$ARGUMENTS` sem implementar código funcional quando executado isoladamente.

## Pré-condição

Usar a auditoria disponível. Se a unidade não estiver auditada, executar primeiro uma análise equivalente e registar as lacunas.

O plano deve ser baseado no **estado real do código e dos testes**, usando `PROJECT_STATE.md`, `ROADMAP.md` e a arquitectura como contexto e contrato. Não planear a partir de componentes que existem apenas na documentação.

## MODO ISOLADO VS. MODO /WSAI-RUN

Quando `/wsai-plan` for executado directamente pelo utilizador, permanece um comando de planeamento: **não implementa** e termina com `READY TO IMPLEMENT` ou `BLOCKED`.

Quando o planeamento for uma etapa interna de `/wsai-run`, o resultado `READY TO IMPLEMENT` é uma autorização operacional suficiente para o orquestrador prosseguir, desde que a unidade já esteja autorizada pelo `PROJECT_STATE.md`/`ROADMAP.md` e não introduza decisão arquitectural material.

**Não existe uma segunda aprovação humana implícita entre `READY TO IMPLEMENT` e `/wsai-implement` dentro de `/wsai-run`.** Pedir confirmação apenas por existir um plano interno contradiz a missão autónoma do orquestrador.

Se o plano detectar uma decisão arquitectural material nova, deve terminar em `BLOCKED` e identificar exactamente a decisão necessária.

## Plano obrigatório

1. Objectivo e critério de conclusão.
2. Estado actual e componentes que já fornecem a responsabilidade.
3. Ficheiros que precisam de ser alterados.
4. Ficheiros novos estritamente necessários.
5. Interfaces/contratos envolvidos.
6. Dependências e direcção das dependências.
7. Impacto no `wsai-run` e no fluxo sequencial.
8. Compatibilidade com comandos `/wsai-*` individuais.
9. Estratégia de migração não destrutiva.
10. Estratégia de rollback.
11. Testes unitários, integração, negativos e regressão.
12. Critérios de validação da unidade.
13. Gate de consolidação necessário, se aplicável (`/wsai-validate`).
14. Documentação a actualizar.
15. Alterações ao `PROJECT_STATE.md`/`IMPLEMENTATION_LOG.md`.
16. Alterações Git previstas.
17. Riscos e condições de paragem.

## Regra especial

Não propor a criação de um novo módulo quando uma responsabilidade equivalente já existir. Preferir extensão, adapter ou integração sobre a substituição.

Não transformar uma lacuna documental num novo componente funcional sem confirmar a necessidade no código e na arquitectura.

## Correcções de gate

Se o `/wsai-run` receber um `NOT APPROVED` causado exclusivamente por uma lacuna documental/processual P2 inequívoca, localizada e sem impacto funcional ou arquitectural, pode criar uma unidade correctiva mínima para fechar o gap. Essa unidade deve incluir apenas os ficheiros necessários à evidência do gate e deve ser revalidada.

Um P0/P1, uma decisão arquitectural material, alteração de requisitos fundamentais ou risco de perda de dados não pode ser convertido artificialmente em correcção autónoma.

## Resultado

Entregar um plano executável por uma unidade pequena e verificável. Se a unidade for demasiado grande, dividi-la antes da implementação.

O plano deve terminar com uma decisão clara:

```text
READY TO IMPLEMENT
```

ou

```text
BLOCKED
Motivo: ...
Decisão necessária: ...
```
