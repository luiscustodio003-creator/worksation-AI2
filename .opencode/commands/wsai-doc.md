---
description: Actualizar documentação e estado do WorkStation AI 2 sem alterar funcionalidade
agent: plan
---
# /wsai-doc — DOCUMENTAÇÃO CONTROLADA

Actualizar documentação da área `$ARGUMENTS` com base em trabalho já validado.

## Regras

- Não inventar estado que não tenha sido validado.
- Não marcar uma fase como concluída sem implementação e testes.
- Manter `PROJECT_STATE.md` coerente com `ROADMAP.md`.
- Registar decisões arquitecturais e motivos.
- Actualizar `IMPLEMENTATION_LOG.md` no fim de cada unidade.
- Manter documentação técnica em português de Portugal.
- Corrigir inconsistências históricas sem reescrever relatórios antigos desnecessariamente.

## Conteúdo mínimo

A documentação da unidade deve indicar:

- objectivo;
- arquitectura abrangida;
- componentes envolvidos;
- dependências;
- alterações efectuadas;
- testes e resultado;
- riscos residuais;
- estado actual;
- próximo passo.

Este comando documenta o estado; não deve aproveitar a tarefa para iniciar uma nova implementação funcional.
