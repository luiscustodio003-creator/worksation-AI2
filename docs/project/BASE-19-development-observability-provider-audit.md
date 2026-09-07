# WORKSTATION AI 2 — AUDITORIA: OBSERVABILIDADE DE DESENVOLVIMENTO E PROVIDER LAYER

## Data

2026-09-08

## Objectivo

Registar a auditoria efectuada após a conclusão da Fase 6, com especial atenção à visibilidade do `/wsai-run` durante a execução e à capacidade actual do Provider Layer para Ollama, llama.cpp e APIs compatíveis.

## 1. Observabilidade do desenvolvimento

Foi identificada uma regressão de observabilidade: o `/wsai-run` mantinha o relatório final e as regras de execução, mas não exigia explicitamente a apresentação contínua de fase, unidade, etapa e próximo passo durante operações demoradas.

### Correcção

Foram actualizados:

- `.opencode/commands/wsai-run.md`
- `.opencode/skills/wsai-development/SKILL.md`

O agente passa a ter uma regra explícita de **visibilidade obrigatória**:

- mostrar o estado no início da execução;
- actualizar em mudanças relevantes de etapa;
- indicar fase, unidade, etapa, progresso, concluído, pendente e próximo passo;
- não inventar percentagens;
- evitar ruído por cada comando trivial.

A disposição exacta do painel lateral continua a ser responsabilidade da interface do OpenCode; o requisito do projecto é garantir que o progresso permanece visível no fluxo do agente.

## 2. Estado do Provider Layer

A Fase 6 está concluída a 100%, com:

- contratos;
- registo;
- detecção;
- adaptadores;
- health checks.

O catálogo actual contém:

1. Ollama — runtime local;
2. llama.cpp — runtime local através do protocolo compatível com OpenAI;
3. API compatível com OpenAI — fornecedor remoto genérico.

## 3. Capacidade actual por fornecedor

### Ollama

Existe `OllamaAdapter` com:

- `GET /api/tags` para listar modelos;
- `POST /api/generate` para geração de texto;
- transporte HTTP injectável;
- tratamento de erros;
- integração com detecção e health checks.

### llama.cpp

Existe suporte através de `OpenAiCompatibleAdapter`, com:

- `GET /v1/models`;
- `POST /v1/chat/completions`;
- catálogo do provider com endpoint local predefinido `http://localhost:8080`.

Isto corresponde ao modo de servidor HTTP compatível com OpenAI utilizado pelo llama.cpp.

### APIs compatíveis com OpenAI

Existe o mesmo adaptador genérico, permitindo reutilizar o contrato para endpoints compatíveis com OpenAI.

## 4. O que está efectivamente validado

Os testes cobrem os protocolos através de transports injectáveis e servidores HTTP locais controlados. A integração real contra uma instalação concreta de Ollama ou llama.cpp não é assumida pelo repositório nem foi declarada como teste de ambiente do utilizador.

Portanto:

**Sim, a arquitectura já está preparada para Ollama e llama.cpp.**

**Não, ainda não devemos afirmar que qualquer instalação concreta está automaticamente pronta para produção sem executar um smoke test no ambiente onde o WSAI 2 corre.**

## 5. Limites actuais que devem ser tratados nas fases seguintes

Estes pontos não invalidam a conclusão da Fase 6, mas devem permanecer explícitos:

- autenticação/cabeçalhos para APIs remotas ainda não fazem parte do adaptador genérico;
- streaming não está implementado no contrato actual;
- cancelamento/stop pertence ao Runtime Engine;
- embeddings ainda não possuem um contrato de execução específico no Provider Layer;
- não existe ainda uma camada completa de descoberta que associe automaticamente cada modelo descoberto pelo provider às definições do Model Registry;
- a selecção final de provider + modelo por tarefa pertence à integração da Task Intelligence;
- métricas de desempenho e benchmarking reais pertencem às fases posteriores e não devem ser inventados pelo catálogo.

## 6. Conclusão arquitectural

O Provider Layer está correctamente separado do Model Intelligence:

```text
Model Intelligence
    ↓
Qual é o modelo adequado?
    ↓
Provider Layer
    ↓
Que fornecedor compatível e saudável o pode disponibilizar?
    ↓
Runtime Engine
    ↓
Como executar, monitorizar, cancelar e gerir recursos?
```

O sistema permanece provider-agnostic no domínio. Ollama e llama.cpp são adaptadores concretos, não dependências estruturais do núcleo.

## 7. Próximo passo

Iniciar a **Fase 7 — Task Intelligence**. A primeira unidade deve definir o contrato de tarefa e a sua representação, antes de introduzir a classificação, requisitos, selecção de capacidades e plano de execução.
