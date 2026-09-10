# WORKSTATION AI 2 — RELATÓRIO DA FASE 3

## RUNTIME INTELLIGENCE

**Subsistema:** `wsai2.runtime`
**Referência arquitectural:** subsistema 3.3
**Roadmap:** Fase 3
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

Enquanto a Fase 2 descreve o que a máquina **suporta**, a Fase 3 descreve o que está **disponível naquele momento**:

> Representa o estado actual dos recursos: memória disponível, carga de CPU/GPU, processos e disponibilidade efectiva.

O sistema precisa de saber, quando toma uma decisão, se existe **agora** memória livre, se a CPU está ocupada, se há processos pesados em curso, há quanto tempo a máquina está ligada. Esta é a **Runtime State** — *o que está disponível agora*.

## 2. ARQUITECTURA DA FASE

```text
wsai2.runtime
  ├── base.py        → contratos: perfil de runtime, disponibilidade
  ├── cpu.py         → carga de CPU
  ├── memory.py      → utilização de memória
  ├── processes.py   → top de processos por memória
  ├── availability.py→ análise derivada de disponibilidade efectiva
  └── factory.py     → discover_runtime(): recolhe o estado real
```

### O perfil de runtime

O `RuntimeProfile` contém:

- **CpuLoad** — carga momentânea;
- **MemoryRuntime** — utilização actual de memória;
- **processos** — top de processos por memória RSS;
- **SystemUptime** — tempo de actividade;
- **disponibilidades derivadas** — scores 0.0–1.0 com estados `HEALTHY`–`CRITICAL` e um `overall_status` ponderado.

A medição usa `psutil`, cross-platform, por trás da plataforma.

## 3. A SEPARAÇÃO FUNDAMENTAL (COMPLETA)

Juntas, as Fases 2 e 3 fecham a primeira grande distinção do projecto:

```text
Hardware Capability   →  O que a máquina é capaz de suportar   (Fase 2)
Runtime State         →  O que está disponível agora            (Fase 3)
```

Um exemplo: a máquina pode **suportar** 32 GB de RAM (Hardware Capability), mas **ter livres** apenas 4 GB neste momento por causa de outras tarefas (Runtime State). O WSAI 2 toma decisões conhecendo ambos.

## 4. CONEXÃO COM A VISÃO

>A visão insiste: "o hardware pode suportar determinada capacidade, mas essa capacidade pode não estar disponível naquele instante devido a memória ocupada, outras tarefas, temperatura, carga, concorrência ou outras restrições. Por isso existem duas perspectivas: Hardware Intelligence e Runtime Intelligence."

A Fase 3 é a **segunda perspectiva** — a consciência do momento presente. É o que torna o sistema verdadeiramente **adaptativo**, porque sabe quando deve adiar, limitar ou condicionar uma tarefa.

## 5. EVIDÊNCIA E VALIDAÇÃO

- Testes: `tests/test_runtime.py` (24 testes na fase, incluindo a análise de disponibilidade).
- `discover_runtime()` devolve o perfil completo e determinístico da máquina actual.
- Alimenta a Fase 4 (Capability Engine — restrições de runtime) e a Fase 5 (Model Intelligence — requisitos de runtime).
- Teste corrigido na fase: `cpu_percent` de processos pode exceder 100% no Windows (portabilidade na prática).

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: saber o que está disponível *neste momento*, não apenas o que existe.
2. Solução: Runtime Intelligence mede carga de CPU, memória em uso, processos e uptime.
3. A medição é cross-platform (atrás da Fase 1) e produz um perfil determinístico.
4. Ideia central: **Hardware Capability ≠ Runtime State** — a Fase 2 diz "pode", a Fase 3 diz "consegue agora".
5. Papel no pipeline: fornece o "Runtime Intelligence" — *o que está disponível neste momento?* — a todos os motores de decisão.