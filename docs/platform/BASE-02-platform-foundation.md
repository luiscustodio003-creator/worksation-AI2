# WORKSTATION AI 2 — RELATÓRIO DA BASE: PLATFORM FOUNDATION

## O que foi feito

Implementou-se o subsistema **Platform Foundation** (Fase 1 do roadmap),
composto pela abstração de plataforma, enumeração de sistemas operativos,
adaptadores concretos para Windows e Linux, e uma fábrica que selecciona
o adaptador adequado ao sistema operativo corrente.

## Onde se encaixa na arquitectura

Corresponde ao subsistema **3.1 Platform Foundation** descrito em
`docs/architecture/ARCHITECTURE.md`. A camada de plataforma isola as
diferenças entre sistemas operativos e fornece acesso controlado a
funcionalidades específicas de Windows e Linux, garantindo que o domínio
não depende de detalhes concretos de infraestrutura.

## Para que serve

- Permitir que o resto da aplicação descubra e interaja com o sistema
  operativo de forma uniforme através de `wsai2.platform.get_platform()`.
- Isolar código específico de Windows (`windows.py`) e Linux (`linux.py`)
  da lógica de domínio e de testes.
- Fornecer uma descrição neutra da plataforma (`PlatformInfo`) para
  consumidores que não precisam de detalhes concretos do SO.

## Ficheiros criados

- `src/wsai2/platform/__init__.py` — interface pública do módulo
- `src/wsai2/platform/base.py` — contratos, enums, `PlatformInfo`,
  `detect_operating_system()`, `build_platform_info()`
- `src/wsai2/platform/windows.py` — adaptador Windows
- `src/wsai2/platform/linux.py` — adaptador Linux
- `src/wsai2/platform/factory.py` — fábrica `get_platform()`
- `tests/test_platform.py` — 5 testes de detecção, descrição e fábrica

## Dependências

- Python ≥ 3.10 (módulos padrão `sys`, `platform`, `dataclasses`, `typing`)
- Nenhuma dependência externa de runtime

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **8 testes aprovados** (3 fundação + 5 platform). Os testes
validam a detecção correcta do SO corrente, a coerência dos marcadores
`is_windows`/`is_linux` em `PlatformInfo`, e a selecção do adaptador
correcto pela fábrica.

## Estado da fase

**Fase 1 — Platform Foundation** — unidade inicial concluída.

Restam na Fase 1 os adaptadores de mais baixo nível (ex.: chamadas WMI
no Windows, `/proc` no Linux) e testes de compatibilidade cruzada,
que serão abordados em unidades subsequentes.

## Próximo passo

Iniciar a **Fase 2 — Hardware Intelligence** (descoberta de CPU, memória,
GPU, armazenamento) sobre a abstração de plataforma agora disponível.