# WORKSTATION AI 2 — DESENVOLVIMENTO CONTROLADO

## Objectivo

Estabelecer o mecanismo oficial para evoluir o WSAI 2 sem destruir ou duplicar o que já está implementado.

A arquitectura actual é a **baseline**. Cada alteração deve ser uma evolução incremental, verificável e reversível.

## Ciclo oficial

```text
AUDITAR
   ↓
PLANEAR
   ↓
IMPLEMENTAR
   ↓
TESTAR
   ↓
DOCUMENTAR
   ↓
GIT
   ↓
VALIDAR ESTADO
```

`/wsai-run` executa este ciclo autonomamente quando a unidade está claramente definida. Os comandos `/wsai-*` permitem executar cada etapa individualmente.

## Regra de não destruição

Antes de criar ou substituir qualquer responsabilidade:

1. procurar o componente existente;
2. confirmar a sua responsabilidade;
3. mapear consumidores e dependências;
4. avaliar impacto;
5. preferir integração, extensão ou adapter;
6. manter a implementação anterior durante a migração;
7. remover código obsoleto apenas numa unidade posterior e após regressão validada.

### Nunca fazer

- criar um segundo `CapabilityRegistry`;
- criar um segundo `ProviderRegistry`;
- duplicar lógica do Task Intelligence dentro do Runtime;
- mover lógica do Core para a UI/API;
- reescrever o `wsai-run` sem migração e regressão;
- introduzir addons como dependências privilegiadas do Core.

## O papel do WSAI-RUN

O `/wsai-run` é o **orquestrador de desenvolvimento**, não o dono de toda a lógica do produto.

O fluxo deve permanecer:

```text
Pre-flight
   ↓
Sincronização
   ↓
Determinação da unidade
   ↓
Planeamento
   ↓
Implementação
   ↓
Validação
   ↓
Documentação/Estado
   ↓
Git
   ↓
Resultado
```

A implementação das futuras fases do produto deve, por sua vez, manter o Runtime como responsável pela execução das tarefas. O comando de desenvolvimento não deve incorporar lógica funcional do produto.

## Autonomia controlada

A autonomia significa continuar sem pedir confirmação para uma unidade já definida e segura. Não significa ignorar limites.

O `/wsai-run` deve parar perante:

- conflito arquitectural material;
- perda ou corrupção potencial de dados;
- conflito Git não resolvível com segurança;
- falha crítica não corrigível;
- requisito novo que altere significativamente a arquitectura.

Pode continuar automaticamente para a unidade seguinte quando esta for pequena, directamente dependente, bem especificada e não introduzir uma decisão arquitectural material.

## Estado persistente

Cada unidade deve deixar informação suficiente para uma nova sessão recuperar o contexto através de:

- `PROJECT_STATE.md` — estado global;
- `ROADMAP.md` — sequência prevista;
- `IMPLEMENTATION_LOG.md` — histórico de implementação;
- relatório específico da base/unidade;
- Git — histórico técnico reversível.

## Visibilidade

A autonomia não elimina observabilidade. Durante o `/wsai-run`, o utilizador deve ver:

- fase;
- unidade;
- etapa;
- progresso real ou estado textual;
- concluído;
- em execução;
- pendente;
- próximo passo.

Não inventar percentagens.

## Baseline actual

No início da preparação da Fase 8, o repositório tem Fase 7 — Task Intelligence concluída e 209 testes aprovados segundo o estado persistente actual. A preparação do Runtime Engine deve começar por uma auditoria, não por uma reescrita.

## Relação com o endurecimento da arquitectura

Os pontos de hardening identificados serão tratados gradualmente:

1. Extension Contract e lifecycle;
2. modelo de erros;
3. Execution Context;
4. Resource Governance;
5. timeout/cancellation/recovery;
6. Runtime Engine e scheduler;
7. versionamento/compatibilidade;
8. security/policy;
9. project isolation;
10. architecture contract tests;
11. integração dos addons sobre estes contratos.

Capability Registry e Provider Registry já existem e serão evoluídos apenas onde a auditoria demonstrar uma lacuna.

## Critério de conclusão

Uma unidade só está concluída quando implementação, testes, revisão arquitectural, documentação, estado persistente e Git estiverem coerentes.
