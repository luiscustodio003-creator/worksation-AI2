# CONSTITUIÇÃO ARQUITECTURAL — WORKSTATION AI 2

## ARTIGO 1 — Responsabilidade

Cada módulo possui uma responsabilidade principal explícita.

## ARTIGO 2 — Dependências

O domínio não depende de detalhes concretos de infraestrutura, interface, API ou fornecedor.

## ARTIGO 3 — Interfaces

Integrações externas devem ocorrer através de contratos ou adaptadores claramente definidos.

## ARTIGO 4 — Sistemas operativos

Código específico de Windows e Linux deve ser isolado numa camada de plataforma.

## ARTIGO 5 — Hardware e runtime

A capacidade estrutural do hardware e o estado momentâneo do runtime são entidades distintas.

## ARTIGO 6 — API

A API é uma camada de apresentação e não o centro da arquitectura.

## ARTIGO 7 — Interface de utilizador

A interface apresenta capacidades reais e consome contratos da aplicação.

## ARTIGO 8 — Crescimento controlado

Não criar módulos, abstrações ou ficheiros sem necessidade demonstrada pela fase actual.

## ARTIGO 9 — Testabilidade

A arquitectura deve permitir testes unitários sem exigir recursos externos sempre que possível.

## ARTIGO 10 — Documentação

Cada módulo relevante deve documentar:

- finalidade;
- responsabilidade;
- limites;
- dependências;
- interfaces públicas;
- comportamento esperado;
- testes associados.

## ARTIGO 11 — Conclusão de uma base

Uma base arquitectural só está concluída quando possui:

- implementação;
- validação;
- testes;
- documentação;
- relatório da fase;
- actualização do estado global.

## ARTIGO 12 — Evolução

Alterações à arquitectura exigem análise de impacto e actualização da documentação correspondente.
