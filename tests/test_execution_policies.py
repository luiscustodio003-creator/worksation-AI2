"""Testes das Políticas de Execução (Fase 8.4).

Valida o subsistema `wsai2.execution`: contratos de timeout e de
recuperação, guards de deadline, execução com timeout (em thread worker),
recuperação por tentativas e a composição centralizada
`execute_with_policies` com cancelamento e reserva de recursos.
"""

import time

import pytest

from wsai2.core import (
    CancellationError,
    CancellationToken,
    ExecutionContext,
    TimeoutError,
    ValidationError,
)
from wsai2.extension import ResourceLimit
from wsai2.execution import (
    DeadlineGuard,
    RecoveryPolicy,
    TimeoutPolicy,
    execute_with_policies,
    run_with_recovery,
    run_with_timeout,
)
from wsai2.resource import ResourceGovernor, ResourceDimension


def _contexto(**kwargs: object) -> ExecutionContext:
    """Constrói um contexto de execução de teste com valores válidos."""
    valores: dict[str, object] = {"execution_id": "exec-1", "task_id": "task-1"}
    valores.update(kwargs)
    return ExecutionContext(**valores)  # type: ignore[arg-type]


class _Relogio:
    """Relógio monotónico determinístico para testes."""

    def __init__(self, valor: float = 1000.0) -> None:
        self._valor = valor

    def __call__(self) -> float:
        return self._valor

    def avancar(self, segundos: float) -> None:
        self._valor += segundos


# --- TimeoutPolicy ---------------------------------------------------------


def test_timeout_policy_ilimitada_por_omissao() -> None:
    """Sem vias de limite, a política deve ser ilimitada."""
    politica = TimeoutPolicy()
    assert politica.is_limited is False
    assert politica.absolute_deadline() is None


def test_timeout_policy_duracao_converte_em_deadline() -> None:
    """A duração deve converter-se em deadline absoluta pelo relógio."""
    politica = TimeoutPolicy(duration_seconds=5.0)
    assert politica.is_limited is True
    assert politica.absolute_deadline(now=100.0) == pytest.approx(105.0)


def test_timeout_policy_deadline_absoluta_directa() -> None:
    """Uma deadline absoluta deve manter-se tal e qual."""
    politica = TimeoutPolicy(deadline=110.0)
    assert politica.absolute_deadline(now=100.0) == 110.0


def test_timeout_policy_rejeita_duas_vias() -> None:
    """Definir duração E deadline em simultâneo deve ser rejeitado."""
    with pytest.raises(ValidationError):
        TimeoutPolicy(duration_seconds=5.0, deadline=110.0)


def test_timeout_policy_rejeita_duracao_negativa() -> None:
    """Duração negativa deve ser rejeitada com ValidationError."""
    with pytest.raises(ValidationError):
        TimeoutPolicy(duration_seconds=-1.0)


# --- DeadlineGuard ---------------------------------------------------------


def test_deadline_guard_mede_tempo_restante() -> None:
    """O guard deve reportar o tempo restante até à deadline."""
    relogio = _Relogio(valor=100.0)
    guard = DeadlineGuard(deadline=110.0, clock=relogio)
    assert guard.remaining_seconds == pytest.approx(10.0)
    assert guard.is_expired is False


def test_deadline_guard_detecta_expiracao() -> None:
    """O guard deve detectar a expiração e levantar TimeoutError."""
    relogio = _Relogio(valor=100.0)
    guard = DeadlineGuard(deadline=100.0, clock=relogio)
    assert guard.is_expired is True
    with pytest.raises(TimeoutError) as exc:
        guard.raise_if_expired()
    assert exc.value.code == "wsai.timeout.exceeded"


# --- run_with_timeout ------------------------------------------------------


def test_run_sem_limite_devolve_resultado() -> None:
    """Sem limite, a execução deve correr sem sobrecarga e devolver."""
    assert run_with_timeout(lambda: 42) == 42


def test_run_com_timeout_devolve_resultado() -> None:
    """Execução rápida dentro da deadline deve devolver o resultado."""
    assert run_with_timeout(
        lambda: "ok", TimeoutPolicy(duration_seconds=5.0)
    ) == "ok"


def test_run_timeout_excedido_levanta() -> None:
    """Execução mais demorada que a deadline deve levantar TimeoutError."""
    with pytest.raises(TimeoutError) as exc:
        run_with_timeout(
            lambda: time.sleep(1.0),
            TimeoutPolicy(duration_seconds=0.05),
        )
    assert exc.value.code == "wsai.timeout.exceeded"


def test_run_propaga_erro_da_funcao() -> None:
    """Erros levantados dentro de fn devem propagar-se tal e qual."""
    def falha() -> None:
        raise ValueError("falha interna")
    with pytest.raises(ValueError, match="falha interna"):
        run_with_timeout(falha, TimeoutPolicy(duration_seconds=1.0))


def test_run_respeita_deadline_do_contexto() -> None:
    """A deadline do ExecutionContext deve ser enforçada sem política."""
    contexto = _contexto(deadline=time.monotonic() + 0.05)
    with pytest.raises(TimeoutError):
        run_with_timeout(lambda: time.sleep(1.0), context=contexto)


def test_run_so_com_controlo_de_cancelamento() -> None:
    """Sem deadline, o contexto só se aplica ao cancelamento."""
    token = CancellationToken()
    token.cancel()
    contexto = _contexto(cancellation=token)
    with pytest.raises(CancellationError):
        run_with_timeout(lambda: "não deve", context=contexto)


# --- RecoveryPolicy --------------------------------------------------------


def test_recovery_policy_estado_inicial() -> None:
    """Política por omissão não repete (max_attempts=1) e valida."""
    politica = RecoveryPolicy()
    assert politica.max_attempts == 1
    assert politica.retry_count == 0
    assert politica.is_retryable(ValueError("x")) is False


def test_recovery_policy_valida() -> None:
    """Parâmetros inválidos devem ser rejeitados com ValidationError."""
    with pytest.raises(ValidationError):
        RecoveryPolicy(max_attempts=0)
    with pytest.raises(ValidationError):
        RecoveryPolicy(base_delay_seconds=-1.0)
    with pytest.raises(ValidationError):
        RecoveryPolicy(backoff_factor=0.5)


def test_recovery_policy_atraso_por_tentativa() -> None:
    """O atraso deve crescer com o factor de backoff."""
    politica = RecoveryPolicy(max_attempts=4, base_delay_seconds=2.0, backoff_factor=2.0)
    assert politica.delay_for_attempt(1) == 0.0
    assert politica.delay_for_attempt(2) == pytest.approx(2.0)
    assert politica.delay_for_attempt(3) == pytest.approx(4.0)
    assert politica.delay_for_attempt(4) == pytest.approx(8.0)


# --- run_with_recovery -----------------------------------------------------


def test_recovery_sucesso_a_segunda_tentativa() -> None:
    """Falhas repetíveis devem permitir sucesso numa tentativa seguinte."""
    chamadas = {"n": 0}

    def instavel() -> int:
        chamadas["n"] += 1
        if chamadas["n"] < 2:
            raise ValueError("temporário")
        return 7

    politica = RecoveryPolicy(max_attempts=3, retry_error_types=(ValueError,))
    assert run_with_recovery(instavel, politica) == 7
    assert chamadas["n"] == 2


def test_recovery_esgota_e_levanta_ultimo_erro() -> None:
    """Esgotadas as tentativas, deve levantar-se o último erro (tipo preservado)."""
    chamadas = {"n": 0}

    def falha() -> None:
        chamadas["n"] += 1
        raise ValueError("persistente")

    politica = RecoveryPolicy(max_attempts=3, retry_error_types=(ValueError,))
    with pytest.raises(ValueError, match="persistente"):
        run_with_recovery(falha, politica)
    assert chamadas["n"] == 3


def test_recovery_nao_repete_erro_nao_repetivel() -> None:
    """Erros fora de retry_error_types não devem ser repetidos."""
    chamadas = {"n": 0}

    def falha() -> None:
        chamadas["n"] += 1
        raise RuntimeError("imprevisto")

    politica = RecoveryPolicy(max_attempts=3, retry_error_types=(ValueError,))
    with pytest.raises(RuntimeError, match="imprevisto"):
        run_with_recovery(falha, politica)
    assert chamadas["n"] == 1


def test_recovery_regista_historico_de_tentativas() -> None:
    """O histórico deve registar cada tentativa e o seu erro."""
    chamadas = {"n": 0}

    def instavel() -> int:
        chamadas["n"] += 1
        if chamadas["n"] < 3:
            raise ValueError("temporário")
        return 1

    historico: list = []
    politica = RecoveryPolicy(max_attempts=3, retry_error_types=(ValueError,))
    run_with_recovery(instavel, politica, history=historico)
    assert len(historico) == 3
    assert historico[0].succeeded is False
    assert historico[1].succeeded is False
    assert historico[2].succeeded is True


def test_recovery_chama_sleeper_entre_tentativas() -> None:
    """O sleeper deve ser chamado com o atraso calculado."""
    esperas: list[float] = []
    chamadas = {"n": 0}

    def instavel() -> int:
        chamadas["n"] += 1
        if chamadas["n"] < 2:
            raise ValueError("temporário")
        return 1

    politica = RecoveryPolicy(
        max_attempts=2, base_delay_seconds=0.25, retry_error_types=(ValueError,)
    )
    run_with_recovery(instavel, politica, sleeper=esperas.append)
    assert esperas == [pytest.approx(0.25)]


# --- execute_with_policies -------------------------------------------------


def test_execute_sem_politicas_corrento() -> None:
    """Sem políticas, deve devolver o resultado directamente."""
    assert execute_with_policies(lambda: "valor") == "valor"


def test_execute_checkpoint_cancelamento() -> None:
    """Contexto cancelado deve abortar antes de executar."""
    token = CancellationToken()
    token.cancel()
    contexto = _contexto(cancellation=token)
    with pytest.raises(CancellationError):
        execute_with_policies(lambda: "não deve", context=contexto)


def test_execute_checkpoint_deadline_expirada() -> None:
    """Deadline já expirada deve abortar com TimeoutError."""
    contexto_valido = _contexto(deadline=time.monotonic() + 10.0)
    assert execute_with_policies(lambda: "amerce", context=contexto_valido) == "amerce"

    contexto = _contexto(deadline=time.monotonic() + 0.05)
    time.sleep(0.1)
    with pytest.raises(TimeoutError):
        execute_with_policies(lambda: "não deve", context=contexto)


def test_execute_timeout_politica() -> None:
    """Execução demorada deve levantar TimeoutError com a política."""
    contexto = _contexto()
    with pytest.raises(TimeoutError):
        execute_with_policies(
            lambda: time.sleep(1.0),
            context=contexto,
            timeout=TimeoutPolicy(duration_seconds=0.05),
        )


def test_execute_recovery_combinada() -> None:
    """A recuperação deve aplicar-se à execução com timeout."""
    chamadas = {"n": 0}
    contexto = _contexto()

    def instavel() -> int:
        chamadas["n"] += 1
        if chamadas["n"] < 2:
            raise ValueError("temporário")
        return 9

    politica = RecoveryPolicy(max_attempts=3, retry_error_types=(ValueError,))
    assert execute_with_policies(
        instavel,
        context=contexto,
        recovery=politica,
    ) == 9


def test_execute_reserva_e_liberta_recursos() -> None:
    """Com governador e budget, a reserva deve existir e ser libertada."""
    from wsai2.hardware import (
        Architecture,
        CpuInfo,
        CpuVendor,
        HardwareProfile,
        MemoryInfo,
    )
    from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile

    _GB = 1024 ** 3
    hardware = HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL, model_name="T", architecture=Architecture.X86_64,
            physical_cores=8, logical_cores=16,
        ),
        memory=MemoryInfo(total_bytes=int(16 * _GB)),
    )
    runtime = RuntimeProfile(
        cpu=CpuLoad(percent=30.0, count=8),
        memory=MemoryRuntime(
            total_bytes=int(16 * _GB),
            available_bytes=int(6 * _GB),
            used_bytes=int(10 * _GB),
            percent=62.5,
        ),
    )
    governador = ResourceGovernor(hardware=hardware, runtime=runtime)
    contexto = _contexto(budget=(ResourceLimit(name="ram_gb", value=2.0),))

    assert execute_with_policies(lambda: "ok", context=contexto, governor=governador) == "ok"
    assert governador.committed_for(ResourceDimension.RAM) == pytest.approx(0.0)
    assert len(governador.outstanding) == 0


def test_execute_libera_recursos_mesmo_com_erro() -> None:
    """A libertação de recursos deve ocorrer mesmo com erro de execução."""
    from wsai2.hardware import (
        Architecture,
        CpuInfo,
        CpuVendor,
        HardwareProfile,
        MemoryInfo,
    )
    from wsai2.runtime import CpuLoad, MemoryRuntime, RuntimeProfile

    _GB = 1024 ** 3
    hardware = HardwareProfile(
        cpu=CpuInfo(
            vendor=CpuVendor.INTEL, model_name="T", architecture=Architecture.X86_64,
            physical_cores=8, logical_cores=16,
        ),
        memory=MemoryInfo(total_bytes=int(16 * _GB)),
    )
    runtime = RuntimeProfile(
        cpu=CpuLoad(percent=30.0, count=8),
        memory=MemoryRuntime(
            total_bytes=int(16 * _GB),
            available_bytes=int(6 * _GB),
            used_bytes=int(10 * _GB),
            percent=62.5,
        ),
    )
    governador = ResourceGovernor(hardware=hardware, runtime=runtime)
    contexto = _contexto(budget=(ResourceLimit(name="ram_gb", value=2.0),))

    def falha() -> None:
        raise RuntimeError("falha de execução")

    with pytest.raises(RuntimeError, match="falha de execução"):
        execute_with_policies(falha, context=contexto, governor=governador)
    assert governador.committed_for(ResourceDimension.RAM) == pytest.approx(0.0)
    assert len(governador.outstanding) == 0