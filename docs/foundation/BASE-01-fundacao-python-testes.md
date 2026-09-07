# WORKSTATION AI 2 — RELATÓRIO DA BASE: FUNDAÇÃO PYTHON E TESTES

## O que foi feito

Estabeleceu-se a fundação Python mínima do WorkStation AI 2 e a configuração
inicial da base de testes, permitindo a validação automatizada do projecto
desde o início do desenvolvimento.

## Onde se encaixa na arquitectura

Esta base corresponde ao ponto inicial da **Fase 0 — Fundação e Governação**
do roadmap. Não implementa nenhum subsistema funcional (Platform Foundation,
Hardware Intelligence, etc.), apenas a infraestrutura técnica mínima que
permitirá validar, de forma automatizada e verificável, cada unidade futura.

## Para que serve

- Permitir a execução de testes unitários com `pytest`;
- Estabelecer a estrutura de pacote `wsai2` para os futuros subsistemas;
- Centralizar a versão do produto numa única fonte (`src/wsai2/version.py`).

## Ficheiros criados

- `pyproject.toml` — configuração do projecto, dependências dev e pytest;
- `src/wsai2/__init__.py` — pacote raiz do produto;
- `src/wsai2/version.py` — versão única do produto (`0.0.1`);
- `tests/__init__.py` — pacote de testes;
- `tests/conftest.py` — fixture partilhada `project_root`;
- `tests/test_foundation.py` — testes da fundação;
- `.gitignore` — regras de ignoramento para Python e IDE.

## Dependências

- Python >= 3.10;
- `pytest >= 8.0` (dependência de desenvolvimento).

## Testes

Executado com:

```text
py -3.12 -m pytest -v
```

Resultado: **3 testes aprovados** (`test_versao_definida`,
`test_formato_versao_semantico`, `test_pacote_importavel`).

## Estado da fase

Fase 0 ainda **EM PROGRESSO**. Esta unidade completa a base de testes do
roadmap da Fase 0. Restam na Fase 0 a política de modelos OpenCode e o
workflow de sincronização Git (já parcialmente documentados nas skills e
comandos existentes).

## Próximo passo

Concluir os restantes itens da Fase 0 (política de modelos e política Git)
ou, estando estes satisfeitos, iniciar a **Fase 1 — Platform Foundation**,
que implementa a detecção do sistema operativo e a abstração de plataforma.
