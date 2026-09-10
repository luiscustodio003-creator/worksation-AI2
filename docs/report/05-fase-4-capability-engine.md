# WORKSTATION AI 2 — RELATÓRIO DA FASE 4

## CAPABILITY ENGINE

**Subsistema:** `wsai2.capability`
**Referência arquitectural:** subsistema 3.4
**Roadmap:** Fase 4
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

Saber quais são as características do computador (Fases 2 e 3) **não é suficiente**. O problema que a Fase 4 resolve é transformar essas características em **capacidades utilizáveis**:

> É necessário transformar características em capacidades. O sistema deixa de trabalhar apenas com especificações e passa a trabalhar com possibilidades reais de execução.

Uma **capacidade** é uma possibilidade concreta de execução — por exemplo, "inferência local", "embeddings", "ML acelerado" ou "processamento leve". O Capability Engine decide se uma capacidade pode ser utilizada combinando hardware estrutural, estado de runtime e disponibilidade:

```text
CPU suporta AVX2
+ memória disponível suficiente
+ runtime compatível
+ provider disponível
= determinada capacidade pode ser utilizada
```

## 2. ARQUITECTURA DA FASE

```text
wsai2.capability
  ├── base.py            → CapabilityDefinition, CapabilityRequirements
  ├── registry.py        → registo central + catálogo base
  ├── evaluation.py      → avaliação contra hardware e runtime
  └── compatibility.py   → relatório consolidado + catálogo disponível
```

### O percurso de decisão

```text
CapabilityDefinition (o que é a capacidade)
  → Registro (quais existem)
  → Avaliação (hardware + runtime)
  → Compatibilidade (veredicto + justificação)
  → Catálogo de capacidades disponíveis
```

### Os veredictos

- **AVAILABLE** — capacidade utilizável;
- **RESTRICTED** — capacidade condicionada (falha de runtime);
- **UNAVAILABLE** — capacidade indisponível (falha estrutural).

Cada veredicto inclui `RequirementCheck` por requisito (RAM total, RAM disponível, núcleos de CPU, GPU, disco) e, no relatório final, uma **justificação em linguagem natural**.

## 3. RESPEITO À CONSTITUIÇÃO

A avaliação separa rigorosamente:

- **Falha estrutural** (hardware não suporta) → `UNAVAILABLE`.
- **Falha de runtime** (estado momentâneo) → `RESTRICTED`.

É a aplicação prática do artigo 5: Hardware Capability e Runtime State continuam sendo entidades distintas mesmo dentro da avaliação de uma capacidade.

## 4. CONEXÃO COM A VISÃO

>A visão diz: "saber quais são as características do computador não é suficiente. É necessário transformar essas características em capacidades utilizáveis. É essa a função do Capability Engine."

No fluxo de decisão, o Capability Engine responde à pergunta *"que capacidades podem realmente ser utilizadas?"*. É a ponte entre o conhecimento do hardware (Fases 2/3) e a escolha de modelos e fornecedores (Fases 5/6).

## 5. EVIDÊNCIA E VALIDAÇÃO

- Testes: `tests/test_capability*.py` (33 testes na fase — definições, registo, avaliação, compatibilidade).
- Catálogo base: inferência local, embeddings, ML acelerado, processamento leve.
- Domínio puro, sem dependências de plataforma (a medição real ficou nas Fases 2/3; aqui só se raciocina sobre perfis).

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: especificações de hardware não são o mesmo que capacidades utilizáveis.
2. Solução: o Capability Engine transforma características em possibilidades reais de execução.
3. Cada capacidade tem requisitos quantificados e é avaliada contra hardware + runtime.
4. Três estados: disponível, condicionada, indisponível — com justificação clara.
5. Papel no pipeline: *que capacidades podem realmente ser utilizadas?* — liga as Fases 2/3 às Fases 5/6/7.