# WORKSTATION AI 2 — RELATÓRIO DA FASE 2

## HARDWARE INTELLIGENCE

**Subsistema:** `wsai2.hardware`
**Referência arquitectural:** subsistema 3.2
**Roadmap:** Fase 2
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

O WSAI 2 parte de um princípio: **"não assumir que todas as máquinas são iguais."** A Fase 2 dá ao sistema a capacidade de **descobrir e descrever** o que a máquina suporta em termos estruturais:

> O sistema deve conhecer, quando aplicável: CPU, arquitectura, cores e threads, instruções suportadas, memória, GPU, armazenamento, sistema operativo e outras características relevantes.

Esta é a **Hardware Capability** — *o que a máquina é capaz de suportar*. Não é o estado momentâneo (isso é a Fase 3). É a fotografia estrutural e estável do computador.

## 2. ARQUITECTURA DA FASE

```text
wsai2.hardware
  ├── base.py       → contratos: CPU, memória, GPU, armazenamento, perfil
  ├── factory.py    → descobre o hardware real da máquina
  └── profile.py    → perfil agregado + capacidades estruturais derivadas
```

### O perfil de hardware

O `HardwareProfile` agrega domínios com scores normalizados 0.0–1.0 e níveis:

```text
compute (CPU)   → score
memory          → score
graphics (GPU)  → score
storage         → score
       ↓
overall_level (MINIMAL ... HIGH_END)
```

Cada domínio é medido e transformado numa **capacidade estrutural** utilizável pelas fases seguintes.

## 3. A SEPARAÇÃO FUNDAMENTAL

Esta fase materializa a **primeira metade** da distinção mais importante do projecto (Constituição, artigo 5):

```text
Hardware Capability      →  o que a máquina SUPORTA (Fase 2)
Runtime State            →  o que está DISPONÍVEL AGORA (Fase 3)
```

O hardware pode suportar uma capacidade e essa capacidade pode não estar disponível num dado momento por memória ocupada, temperatura, carga ou concorrência. Por isso existe a Fase 3 — e por isso as duas nunca se fundem num único conceito.

## 4. COMPONENTES PRINCIPAIS

- **CPU** — arquitectura, cores, threads, instruções, frequência.
- **Memória** — total, tipo, limitações.
- **GPU** — presença, modelo, memória, capacidade.
- **Armazenamento** — espaço, tipo.
- **`HardwareProfile`** — perfil agregado com capacidades estruturais e resumos textuais de apresentação.

O domínio é **puro**: a descoberta real (medição) é isolada do raciocínio sobre o perfil.

## 5. CONEXÃO COM A VISÃO

>A visão afirma que "o WSAI2 deve compreender a máquina e adaptar a utilização da IA às condições reais" e que "não começamos pelo modelo — começamos pela máquina, pela tarefa e pelo que é realmente possível fazer."

A Fase 2 é **o primeiro passo desse caminho**: o sistema conhece a máquina antes de conhecer qualquer modelo. É o "Hardware Intelligence" do fluxo de decisão: *o que esta máquina suporta?*

## 6. EVIDÊNCIA E VALIDAÇÃO

- Testes: `tests/test_hardware.py` (17 testes na fase).
- Perfil completo com scores, níveis e `overall_level` ponderado.
- Alimenta directamente a Fase 4 (Capability Engine — avaliação) e a Fase 5 (Model Intelligence — compatibilidade estrutural).

## 7. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: o sistema não pode assumir que todas as máquinas são iguais.
2. Solução: Hardware Intelligence descobre e descreve CPU, memória, GPU e armazenamento.
3. O resultado é o `HardwareProfile` — a **capacidade estrutural** da máquina.
4. Ideia-chave do projecto: isto é *o que a máquina suporta*; não é *o que está disponível agora*.
5. A Fase 3 (Runtime Intelligence) completa essa separação: *Hardware Capability ≠ Runtime State*.