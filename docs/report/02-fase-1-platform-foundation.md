# WORKSTATION AI 2 — RELATÓRIO DA FASE 1

## PLATFORM FOUNDATION

**Subsistema:** `wsai2.platform`
**Referência arquitectural:** subsistema 3.1
**Roadmap:** Fase 1
**Estado actual:** IMPLEMENTADA

---

## 1. FINALIDADE E PROBLEMA QUE RESOLVE

O WSAI 2 deve funcionar em **Windows e Linux** sem misturar responsabilidades. O problema que a Fase 1 resolve é o isolamento de tudo o que é específico do sistema operativo:

> O código de domínio não pode saber como o Windows ou o Linux expõem um recurso. A lógica de negócio recebe **contratos e dados normalizados**; a plataforma fornece a informação concreta.

Sem esta fase, qualquer consulta de sistema (uptime, rede, processos) arrastaria lógica `if Windows: ... elif Linux: ...` para dentro de módulos que deveriam ser puros e portáveis.

## 2. ARQUITECTURA DA FASE

```text
wsai2.platform
  ├── base.py        → abstração e contratos comuns
  ├── windows.py     → adaptador Windows (isolado)
  ├── linux.py       → adaptador Linux (isolado)
  └── factory.py     → get_platform(): escolhe o adaptador certo
```

A regra central (Constituição, artigo 4):

- **Windows e Linux nunca se importam mutuamente.**
- **A única entrada para a plataforma é `get_platform()`.**
- O código de SO fica inacessível fora do pacote `platform` — verificado por testes de arquitectura (artigo 4, Fase 8.7).

## 3. COMPONENTES PRINCIPAIS

- **`PlatformInfo`** — superfície pública com informação normalizada da plataforma.
- **`get_platform()`** — ponto único de entrada; a fábrica selecciona o adaptador adequado ao SO corrente.
- **Adaptadores Windows e Linux** — implementam o mesmo contrato; testáveis de forma controlada independentemente do SO em execução.

## 4. CONEXÃO COM A VISÃO

>A visão diz: "a lógica de negócio não deve precisar de saber como o Windows ou o Linux expõem determinado recurso. A plataforma fornece a informação concreta. O Core recebe contratos e dados normalizados."

A Fase 1 é a materialização dessa regra. Torna o projecto **multiplataforma por arquitectura**, não por corrigenda. É o primeiro "motor" a ficar atrás de um contrato — o padrão que se repete em todas as fases seguintes (tudo o que é concreto fica isolado atrás de contratos).

## 5. EVIDÊNCIA E VALIDAÇÃO

- Detecção correcta do SO na máquina de desenvolvimento actual.
- Adaptador Linux presente e testável.
- Testes: `tests/test_platform.py` (5 testes, fase inicial com 3 da fundação).
- Testes de contrato arquitectural verificam que os adaptadores de SO são inacessíveis fora de `platform` e que Windows/Linux não se importam entre si.

## 6. IDEIAS-CHAVE PARA VÍDEO (NOTEBOOKLM)

1. Problema: tornar o sistema multiplataforma sem espalhar lógica `if Windows/Linux` pelo código.
2. Solução: camada de plataforma com um contrato único e dois adaptadores isolados.
3. A entrada única é `get_platform()`; o domínio nunca fala directamente com o SO.
4. É o primeiro exemplo da estratégia central do projecto: **concreto atrás de contrato**.
5. Testável: os adaptadores podem ser testados sem dependerem da máquina real.