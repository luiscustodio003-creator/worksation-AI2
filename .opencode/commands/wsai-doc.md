---
description: Actualizar documentação e estado do WorkStation AI 2 sem alterar funcionalidade
agent: plan
---
# /wsai-doc — DOCUMENTAÇÃO CONTROLADA

Actualizar documentação da área `$ARGUMENTS` com base em trabalho já validado.

## Contrato de transição

Ler `docs/architecture/COMMAND_EXECUTION_CONTRACT.md`.

Durante a reestruturação do Kernel, a documentação deve distinguir claramente:

- estado actual;
- arquitectura target;
- migração em curso;
- responsabilidades já migradas;
- responsabilidades ainda legadas;
- contratos activos;
- riscos residuais.

Nunca documentar a arquitectura target como se já estivesse implementada.

## Regras

- Não inventar estado.
- Não marcar fase concluída sem evidência.
- Manter `PROJECT_STATE.md` coerente com `ROADMAP.md`.
- Registar decisões arquitecturais e motivos.
- Actualizar `IMPLEMENTATION_LOG.md` por unidade.
- Documentar dependências e fronteiras.
- Manter português de Portugal.

## Conteúdo mínimo da unidade

- objectivo;
- arquitectura actual e target quando aplicável;
- classificação da alteração;
- componentes envolvidos;
- consumidores/dependências;
- alterações efectuadas;
- testes e resultado;
- riscos/rollback;
- estado actual;
- próximo passo.

Este comando documenta trabalho validado; não inicia nova implementação funcional.
