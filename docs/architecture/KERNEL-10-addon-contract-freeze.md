# WORKSTATION AI 2 — RELATÓRIO DA UNIDADE: KERNEL-10 — CONTRATO DE ADDON

## O que foi feito

Foi congelado e versionado o **contrato de addon** do WorkStation AI 2: a
superfície pública de `wsai2.extension` (`__all__`, 10 símbolos) fica fixada
por teste de contrato, ganha uma constante de versão da camada
(`EXTENSION_CONTRACT_VERSION = "1.0"`), e os consumidores em `src` ficam
obrigados a importar apenas ao nível do pacote (`wsai2.extension`), nunca
módulos internos.

Foi também registada a decisão material de âmbito que o planeamento detectou:
o título original "Addon SDK / Projects foundation" tinha três leituras
possíveis, e **não se construiu** um pacote SDK novo (duplicaria a
responsabilidade que já vive em `wsai2.extension`) nem **código de Projects**
(é addon futuro que consome o Core — sec. 9 do alvo — e não parte do núcleo).

## Onde se encaixa na arquitectura

- **Fechar a sequência KERNEL-01..KERNEL-10:** o núcleo fica com contratos
  públicos versionados (KERNEL-03..06), firewall de dependências
  (KERNEL-04), fonte única de contratos (KERNEL-07), consumidores do core só
  via `core.public` (KERNEL-08), implementação pesada fora do núcleo
  (KERNEL-09) e, agora, o contrato que os addons devem seguir para
  autor/admitir capacidades (KERNEL-10).
- **Camada addon, não subsistema do kernel:** `extension` permanece fora de
  `KERNEL_SUBSISTEMAS` (core/execution/resource/runtime_engine/security). É a
  fronteira addon→kernel: define o contrato que os addons declaram e o
  núcleo valida (Gate BASE-33).
- **Sem arestas novas:** `extension→{core,security}` e
  `infrastructure→extension` já estavam autorizadas em `FRONTEIRAS`/`FIREWALL`.
  Nenhuma dependência funcional mudou.

## Contrato de addon (o "SDK" do kernel)

Para **autores de addons**, o contrato é:

1. **Importar sempre** de `wsai2.extension` (nível do pacote) e de
   `wsai2.core.public`; nunca módulos internos (`wsai2.extension.registry`,
   `wsai2.core.errors`, etc.) nem outros addons.
2. **Respeitar a versão** `EXTENSION_CONTRACT_VERSION = "1.0"` — revisão da
   superfície só com bump deliberado, detectado no gate.
3. **Declarar** `ExtensionContract` (identidade, tipo, capacidades,
   dependências, recursos, permissões) e passar pela admissão do
   `ExtensionRegistry` com a ponte `permissions → PolicyEngine` (Gate BASE-33);
   as permissões declaradas são concedidas como acções exactas ao
   `principal = id` da extensão.
4. **Contrato de composição:** o criador do runtime fornece o `PolicyEngine`
   (`Scheduler.run(..., policy=...)`); planos de extensões levam
   `principal = id` da extensão no `ExecutionContext`.

`SUPPORTED_CONTRACT_VERSION = "1.0"` permanece na superfície por desígnio: é o
número **semântico** do contrato addon→core (já coberto por
`test_extension_versioning.py`), distinto da constante de manutenção da
camada `EXTENSION_CONTRACT_VERSION`, que fica fora do `__all__` como nas
restantes fronteiras do kernel.

## Decisões registadas

1. **Âmbito A (confirmado pelo utilizador):** congelar o contrato de addon em
   `wsai2.extension`; sem novo subsistema SDK.
2. **Projects fora do núcleo:** nenhum código de Projects é criado no kernel —
   é addon futuro (alvo, sec. 9) que consome o Core. A "fundação de Projects"
   é um marco documental, não um componente.
3. **`extension` como camada addon:** fora de `KERNEL_SUBSISTEMAS`; a versão
   da superfície é controlada na fonte única por tabelas próprias
   (`ADDON_CONTRATO_*`).

## Ficheiros alterados

- `tests/architecture_contracts.py` — tabelas novas: `ADDON_CONTRATO_MODULO`,
  `ADDON_CONTRATO_SUPERFICIE` (10 símbolos), `ADDON_CONTRATO_CONSTANTE_VERSION`,
  `ADDON_CONTRATO_VERSION`.
- `src/wsai2/extension/__init__.py` — `EXTENSION_CONTRACT_VERSION = "1.0"`
  (fora do `__all__`; `SUPPORTED_CONTRACT_VERSION` mantido).
- `tests/test_boundary_kernel.py` — `test_contrato_de_addon_congelado` e
  `test_consumidores_extension_apenas_nivel_pacote`.
- `docs/project/PROJECT_STATE.md`; `docs/project/IMPLEMENTATION_LOG.md`;
  `docs/architecture/CORE_KERNEL_TARGET.md` (sec. 12: KERNEL-10 ✓).

## Testes

```text
py -3.12 -m pytest      →   506 passed, failures=0, errors=0, skipped=0
```

(504 bases + 2 da unidade.) Nenhuma mexida em `FRONTEIRAS`/`FIREWALL`, `src`
além do `extension/__init__.py`, ou testes de domínio — regressão intacta.

## Estado da sequência

A primeira sequência de trabalho do kernel está **concluída
(KERNEL-01..KERNEL-10)**. A migração continua em `core-hardening-foundation`
numa fase de consolidação/release; API e UI permanecem subsistemas futuros
(Fases 10–11), e Projects é o addon inaugural previsto que deve consumir este
contrato.

## Próximo passo

Fecho do estado de transição (release notes do kernel) ou decisão sobre a
primeira capacidade consumidora real do contrato de addon (Project / API).