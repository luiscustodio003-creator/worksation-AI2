# WORKSTATION AI 2 — REGRAS GLOBAIS PARA AGENTES

## 1. Missão

Construir o WorkStation AI 2 de forma incremental, verificável, modular e coerente com a arquitectura oficial.

## 2. Fonte de verdade

Antes de implementar, consultar:

1. `docs/project/PROJECT_STATE.md`
2. `docs/project/ROADMAP.md`
3. `docs/architecture/ARCHITECTURE.md`
4. `docs/architecture/CONSTITUTION.md`
5. documentação dos módulos afectados
6. estado Git e testes existentes

## 3. Regras obrigatórias

1. Nunca implementar uma nova responsabilidade sem verificar se já existe um módulo responsável.
2. Nunca criar módulos vazios apenas para antecipar necessidades futuras.
3. Cada módulo deve possuir uma responsabilidade claramente documentada.
4. Dependências devem respeitar as fronteiras arquitecturais.
5. O código específico de Windows ou Linux deve permanecer isolado da lógica de domínio.
6. Hardware Capability e Runtime State não devem ser confundidos.
7. API e interface não devem conter lógica central de negócio.
8. Cada funcionalidade relevante deve possuir testes adequados.
9. Cada módulo implementado deve possuir documentação detalhada, incluindo responsabilidade, dependências e interfaces.
10. Comentários e documentação técnica devem ser escritos em português de Portugal, salvo quando um formato técnico externo exigir inglês.
11. Antes de declarar uma tarefa concluída, executar a validação aplicável.
12. Actualizar `PROJECT_STATE.md` e `IMPLEMENTATION_LOG.md` no final de cada unidade de trabalho.

## 4. Desenvolvimento por fases

Não saltar fases arquitecturais sem justificação documentada.

Uma fase só é considerada concluída após:

- implementação;
- testes;
- revisão arquitectural;
- documentação;
- relatório da base concluída;
- actualização do estado do projecto;
- validação do estado Git.

## 5. Política de alterações

Antes de modificar código estruturalmente relevante:

- identificar ficheiros afectados;
- identificar dependências;
- verificar riscos de regressão;
- manter alterações concentradas na unidade de trabalho actual.

## 6. Git

Nunca assumir que o repositório local e remoto estão sincronizados.

Antes de iniciar trabalho:

- verificar `git status`;
- verificar a branch;
- obter informação remota quando disponível;
- detectar alterações pendentes.

Antes de concluir trabalho:

- rever o diff;
- executar testes;
- confirmar documentação;
- criar commit apenas para uma unidade coerente de trabalho;
- sincronizar com o remoto quando autorizado pelo ambiente e sem conflitos.

## 7. OpenCode

O OpenCode é uma ferramenta de desenvolvimento do projecto e não uma dependência funcional do produto WSAI 2.

Os modelos disponíveis devem ser escolhidos de acordo com a natureza da tarefa e a configuração efectiva disponível no ambiente OpenCode.

## 8. Regra de paragem

Parar e reportar quando existir:

- conflito arquitectural;
- falha crítica de testes;
- risco de perda de dados;
- conflito Git que não possa ser resolvido com segurança;
- ambiguidade que altere significativamente a arquitectura.
