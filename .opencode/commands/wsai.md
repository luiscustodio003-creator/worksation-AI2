---
description: Menu WSAI 2 — comandos de desenvolvimento disponíveis
---
# /wsai — CENTRO DE COMANDOS WSAI 2

Este comando apresenta o conjunto oficial de comandos de desenvolvimento do WorkStation AI 2.

## Comandos

- `/wsai` — mostra este catálogo e as regras de utilização.
- `/wsai-run` — executa autonomamente uma unidade de desenvolvimento através do ciclo completo: pre-flight → sincronização → determinação → planeamento → implementação → validação → documentação → Git → resultado.
- `/wsai-audit [área]` — audita o estado actual sem alterar código, identificando o que já existe, o que é parcial e o que falta.
- `/wsai-plan [unidade]` — transforma uma unidade auditada num plano de implementação controlado, com impacto, dependências, testes, documentação e rollback.
- `/wsai-implement [unidade]` — implementa apenas uma unidade previamente definida. Não deve saltar a auditoria/planeamento quando estes ainda não existem.
- `/wsai-test [alvo]` — executa e analisa a validação adequada, corrigindo falhas relacionadas com o âmbito quando for seguro.
- `/wsai-validate [modo]` — executa uma validação formal e não destrutiva de módulos, integrações ou da fundação completa, produzindo uma decisão e o próximo comando recomendado.
- `/wsai-doc [área]` — actualiza documentação e estado sem introduzir alterações funcionais não planeadas.
- `/wsai-git` — revê diff, estado, coerência da unidade e prepara/sincroniza Git de forma segura.

## Regra principal

`/wsai-run` é o orquestrador autónomo. Os restantes comandos são etapas independentes que também podem ser executadas manualmente.

Nenhum comando deve assumir que uma responsabilidade está ausente sem primeiro verificar o estado real do projecto.

## Modos de validação

```text
/wsai-validate module <nome>
/wsai-validate integration
/wsai-validate foundation
/wsai-validate full
```

A validação não substitui o desenvolvimento normal e não deve alterar código funcional para fazer uma verificação passar.

## Ordem recomendada para uma alteração nova

```text
/wsai-audit
      ↓
/wsai-plan
      ↓
/wsai-implement
      ↓
/wsai-test
      ↓
/wsai-doc
      ↓
/wsai-git
```

Depois de uma correcção relevante ou no encerramento de um conjunto de núcleos:

```text
/wsai-validate
```

Ou, quando a unidade já está suficientemente definida e é segura para execução autónoma:

```text
/wsai-run
```

## Protecções

- Não substituir componentes existentes sem análise de impacto.
- Não duplicar Capability Registry, Provider Registry ou outras responsabilidades já existentes.
- Não alterar o comportamento do `wsai-run` sem preservar a sua autonomia e visibilidade.
- Não fazer alterações destrutivas para antecipar addons futuros.
- Não declarar uma fundação aprovada apenas porque os testes existentes passaram.
- Não fazer a validação corrigir silenciosamente o código auditado.
- Parar perante conflito arquitectural, risco de perda de dados, conflito Git inseguro ou decisão material não definida.
- Cada unidade deve terminar com testes, documentação, estado persistente e Git coerentes.

## Princípio de evolução

```text
AUDITAR → PLANEAR → IMPLEMENTAR → TESTAR → DOCUMENTAR → SINCRONIZAR
```

## Princípio de consolidação

```text
VALIDAR → CLASSIFICAR → CORRIGIR CONTROLADAMENTE → RETESTAR → REVALIDAR
```

A arquitectura existente é a baseline. A evolução deve ser incremental e não destrutiva.
