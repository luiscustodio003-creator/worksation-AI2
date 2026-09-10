# WORKSTATION AI 2 — RELATÓRIO DA FASE 5

## MODEL INTELLIGENCE

**Subsistema:** `wsai2.model`
**Referência arquitectural:** subsistema 3.5
**Roadmap:** Fase 5
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

Um modelo não é apenas "um nome" ou "um ficheiro". O problema que a Fase 5 resolve é dar ao sistema **conhecimento sobre os modelos**: os seus requisitos, compatibilidade e adequação a cada tarefa.

> A pergunta deixa de ser "qual é o modelo que tenho instalado?" e passa a ser "qual dos modelos que posso utilizar é mais adequado para esta tarefa e para as condições actuais?"

O Model Intelligence analisa:

- tipo de modelo;
- requisitos;
- compatibilidade;
- categoria;
- adequação à tarefa;
- recursos disponíveis;
- alternativas possíveis.

## 2. ARQUITECTURA DA FASE

```text
wsai2.model
  ├── base.py            → ModelDefinition, ModelKind, ModelMetadata, ModelRequirements
  ├── registry.py        → registo central + catálogo base
  ├── compatibility.py   → avaliação contra capacidades, hardware e runtime
  ├── classification.py  → categoria funcional + score de adequação
  └── recommendation.py  → recomendação do modelo mais adequado
```

### O percurso de decisão

```text
Registo e metadados (o que são os modelos)
  → Requisitos (de que precisam)
  → Compatibilidade (satisfazem a máquina e a tarefa?)
  → Classificação (categoria funcional + score)
  → Recomendação (a melhor escolha justificada)
```

### Os três estados de um modelo

- **AVAILABLE** — utilizável;
- **RESTRICTED** — condicionado (capacidade condicionada ou runtime insuficiente);
- **UNAVAILABLE** — indisponível (capacidade em falta ou requisito estrutural falhado).

## 3. A INDEPENDÊNCIA MODELO / FORNECEDOR

Esta fase fixa a segunda grande separação do projecto (Constituição, artigo 13):

> "Qual modelo usar" (Model Intelligence) e "através de que fornecedor executar" (Provider Layer) são **decisões distintas**.

O Model Intelligence decide a **adequação** do modelo; o Provider Layer determina **através de que fornecedor** esse modelo pode ser disponibilizado. Um modelo pode não ser recomendado agora e ser recomendado mais tarde, ou ser executável por vários fornecedores — sem que isso afecte a regra de recomendação.

## 4. CONEXÃO COM A VISÃO

>A visão diz: "o modelo também não deve ser tratado apenas como um nome ou um ficheiro. Cada modelo possui requisitos, características e adequação a diferentes tarefas."

A Fase 5 é o "Model Intelligence" do fluxo: *que modelo é adequado?* — consultado depois do Capability Engine saber *quais capacidades podem realmente ser utilizadas*. Os catálogos são agnósticos a fornecedor (por exemplo, Qwen 2.5, Phi-3 Mini, All MiniLM L6 v2).

## 5. EVIDÊNCIA E VALIDAÇÃO

- Testes: `tests/test_model*.py` (42 testes na fase — registo, compatibilidade, classificação, recomendação).
- Política de recomendação determinística documentada: candidatos com score > 0, ordenados por score, parâmetros, RAM e id.
- Modelos indisponíveis nunca são recomendados.
- Domínio puro, sem dependências de plataforma.

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: um modelo é mais do que um nome — tem requisitos, compatibilidade e adequação.
2. Solução: Model Intelligence regista, avalia, classifica e recomenda modelos com justificação.
3. Três estados: disponível, condicionado, indisponível — nunca se recomenda o que não pode correr.
4. Ideia central: **modelo ≠ fornecedor**. O Model Intelligence escolhe o modelo; o Provider Layer (Fase 6) escolhe o motor.
5. Papel no pipeline: *que modelo é adequado para esta tarefa e estas condições?*