# WSAI 2 — Command Execution Contract

## Objectivo

Definir o contrato comum dos comandos `/wsai-*` durante a evolução do Core/Kernel e, posteriormente, dos Addons.

Este documento protege a execução autónoma contra alterações estruturais, dependências ocultas e migrações destrutivas.

## Estado de arquitectura

Os comandos devem reconhecer sempre o estado actual do projecto:

```text
LEGACY      = arquitectura anterior ainda em utilização
TRANSITION  = migração controlada entre arquitectura actual e target
TARGET      = arquitectura target operacional
FROZEN      = núcleo estabilizado; alterações passam por evolução formal
```

Durante a reestruturação do Kernel, o estado esperado é `TRANSITION`.

## Princípio fundamental

Os comandos operam sobre responsabilidades e contratos, não sobre a estrutura física dos directórios.

Antes de criar, mover, dividir, fundir ou eliminar código, devem determinar:

1. responsabilidade actual;
2. consumidores;
3. dependências;
4. contrato exposto;
5. testes afectados;
6. destino arquitectural;
7. estratégia de rollback.

## Classificação obrigatória de alterações

Toda alteração estrutural deve ser classificada como:

```text
CREATE
ADAPT
MOVE
SPLIT
MERGE
DEPRECATE
DELETE
FREEZE
```

`DELETE` só é permitido depois de demonstrar que não existem consumidores, que a substituição está validada e que o rollback está definido.

## Before Extend

Antes de criar uma responsabilidade nova:

```text
Existe implementação equivalente?
        ├── SIM → reutilizar / adaptar / integrar
        └── NÃO → justificar criação
```

Não criar implementações paralelas para responsabilidades já existentes.

## Regras de migração

Durante `TRANSITION`:

- preservar comportamento validado;
- preferir adapter/fachada sobre ruptura imediata;
- migrar por unidades pequenas;
- testar depois de cada unidade estrutural;
- manter documentação sincronizada;
- criar checkpoint Git por unidade coerente;
- não apagar a origem antes da validação do destino;
- não alterar simultaneamente várias fronteiras arquitecturais sem necessidade;
- nunca remover superfícies públicas já versionadas; extrair do núcleo apenas a implementação pesada, por trás dos contratos públicos.

## Dependency Firewall

```text
Application → Core Public API
Addon       → Core Public API
Infrastructure → contratos/ports definidos
Core        → não depende de Application nem Addons
Addon       → não depende directamente de outro Addon
```

Dependências fora destas regras exigem decisão arquitectural explícita.

## Autoridade

```text
PROJECT_STATE.md / ROADMAP.md
        ↓
ARCHITECTURE.md + contracts
        ↓
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

`/wsai-run` orquestra este ciclo e não pode contrariar os contratos acima.

## Condições de paragem

A execução autónoma deve parar perante:

- decisão arquitectural material não definida;
- alteração de requisitos fundamentais;
- risco significativo de perda/corrupção de dados;
- conflito Git que não possa ser resolvido com segurança;
- falha técnica sem correcção segura;
- violação detectada do Dependency Firewall que exija decisão.

Não deve parar apenas por encontrar um plano `READY TO IMPLEMENT` ou um gate `APPROVED WITH WARNINGS`.

## Estado de cada unidade

Uma unidade só pode ser marcada como concluída quando existir evidência suficiente de:

```text
AUDIT → PLAN → IMPLEMENT → TEST → VALIDATE → DOC → GIT
```

O `PROJECT_STATE.md` deve reflectir o estado real e nunca antecipar a conclusão.

## Compatibilidade durante a transição

Os comandos individuais continuam utilizáveis. `/wsai-run` pode encadear os mesmos passos autonomamente, mas não deve duplicar regras contraditórias.

Qualquer comando novo ou alterado deve respeitar este contrato.
