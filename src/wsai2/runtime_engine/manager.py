"""Gestor de execução de planos (hardening 07 do CORE_HARDENING_PLAN).

O ``RuntimeManager`` executa um ``ExecutionPlan`` produzido pelo Task
Intelligence (Fase 7). O plano inteiro é executado numa única chamada a
``execute_with_policies`` (Fase 8.4): o checkpoint inicial, o timeout
efectivo, a recuperação (retry) e a reserva/libertação de orçamento no
``ResourceGovernor`` (Fase 8.3) aplicam-se ao plano **como unidade**.

Cada passo do plano é observado como um ``StepOutcome`` (monitorização):
num plano concluído, todos os passos têm estado ``SUCCESS``; na primeira
falha, o passo falha fica ``FAILED`` e os restantes ``SKIPPED`` (não
executados), preservando a cobertura integral do plano no relatório.

Responsabilidades:

- validar o plano (executável) e a coerência com o contexto;
- construir o contexto por omissão quando não é fornecido;
- executar o plano com as políticas centralizadas da Fase 8;
- produzir o ``ExecutionReport`` (Execution Result) com métricas por passo.

Fora de âmbito desta unidade: agendamento de múltiplos planos (8.5 —
``scheduler.py``), lifecycle de extensões (8.6) e contacto com
modelos/fornecedores (Provider/Model Runtime — o gestor chama o
``step_runner`` injectado e não conhece fornecedores).
"""

from __future__ import annotations

import functools
import time
from typing import TYPE_CHECKING, Any, Callable

from wsai2.core.context import ExecutionContext
from wsai2.core.errors import (
    CancellationError,
    ExecutionError,
    TimeoutError,
    ValidationError,
    WsaiError,
)
from wsai2.execution import execute_with_policies
from wsai2.security import PolicyEngine, denied_decision
from wsai2.task import ExecutionPlan

from .base import ExecutionReport, ExecutionStatus, StepOutcome, StepRunner, StepStatus

if TYPE_CHECKING:
    from wsai2.execution import RecoveryPolicy, TimeoutPolicy
    from wsai2.resource import ResourceGovernor
    from wsai2.security import PolicyDecision


def _passo_vazio(indice: int, passo: str) -> None:
    """Runner por omissão: sem operação, apenas observa o passo.

    O operador do runtime deve fornecer um runner que realize o passo
    (ex.: invocação do modelo via fornecedor). Sem runner, a execução
    valida o fluxo, as políticas e a observabilidade sem trabalho
    efectivo.
    """


def _erro_wsai(problema: BaseException) -> WsaiError:
    """Normaliza um erro para a taxonomia (wsai2.core.errors).

    Erros já taxonómicos passam intactos; erros genéricos são
    embrulhados num ``ExecutionError`` preservando a mensagem e a origem.
    """
    if isinstance(problema, WsaiError):
        return problema
    return ExecutionError(
        f"passo falhou com {type(problema).__name__}: {problema}",
        code="wsai.execution.step_failed",
        details={"tipo": type(problema).__name__},
    )


class RuntimeManager:
    """Executa planos de execução com as políticas centralizadas.

    A instância é stateless em relação aos planos (pode ser partilhada);
    apenas o governador de recursos, quando fornecido, mantém estado de
    reservas.
    """

    def __init__(
        self,
        *,
        governor: ResourceGovernor | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Cria um gestor de execução.

        Args:
            governor: governador de recursos (8.3) para reservar o orçamento
                do contexto (opcional).
            sleeper: função de espera entre tentativas (injectável).
            clock: relógio monotónico para medir durações (injectável).
        """
        self._governor = governor
        self._sleeper = sleeper
        self._clock = clock

    def execute_plan(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext | None = None,
        *,
        step_runner: StepRunner | None = None,
        timeout: TimeoutPolicy | None = None,
        recovery: RecoveryPolicy | None = None,
        policy: PolicyEngine | None = None,
    ) -> ExecutionReport:
        """Executa um plano de execução e devolve o relatório.

        Args:
            plan: plano a executar (deve ser executável).
            context: contexto de execução; se omisso, é criado um com
                ``execution_id`` derivado do plano.
            step_runner: executor de cada passo (índice, descrição); por
                omissão, sem operação.
            timeout: política de timeout adicional à deadline do contexto.
            recovery: política de recuperação (retry) do plano.
            policy: motor de política (8.8) aplicado **antes do passo 1**;
                sem motor, nenhuma autorização é aplicada (comportamento
                preservado).

        Returns:
            O relatório da execução, sempre (mesmo em falha, timeout,
            cancelamento ou negação de política — a inspecção usa
            ``report.status`` e ``report.error``).

        Raises:
            ExecutionError: se o plano não for executável.
            ValidationError: se o argumento não for um plano, o contexto
                referir outra tarefa ou, com ``policy`` fornecida, faltar
                principal/projecto no contexto.
        """
        if not isinstance(plan, ExecutionPlan):
            raise ValidationError(
                "executar exige um ExecutionPlan",
                code="wsai.execution.plan",
            )
        if not plan.is_executable:
            raise ExecutionError(
                f"plano não executável: {plan.task_id}",
                code="wsai.execution.not_executable",
                details={"motivos": "; ".join(plan.reasons)},
            )
        if context is not None and context.task_id != plan.task_id:
            raise ValidationError(
                "o contexto e o plano referem tarefas diferentes",
                code="wsai.execution.task_mismatch",
                details={"contexto": context.task_id, "plano": plan.task_id},
            )

        contexto = context or ExecutionContext(
            execution_id=f"exec-{plan.task_id}",
            task_id=plan.task_id,
        )
        runner = step_runner if step_runner is not None else _passo_vazio
        passos: list[StepOutcome] = []
        inicio = self._clock()

        decisao: PolicyDecision | None = None
        if policy is not None:
            if not contexto.principal:
                raise ValidationError(
                    "política fornecida exige um principal no contexto",
                    code="wsai.security.principal",
                    details={"execution_id": contexto.execution_id},
                )
            if not contexto.project_id:
                raise ValidationError(
                    "política fornecida exige um project_id no contexto",
                    code="wsai.security.project",
                    details={"execution_id": contexto.execution_id},
                )
            decisao = policy.decide(
                principal=contexto.principal,
                project_id=contexto.project_id,
                action="execute",
            )

        try:
            if decisao is not None and not decisao.allowed:
                posicoes = range(len(plan.steps))
                passos.extend(
                    StepOutcome(
                        index=indice,
                        step=plan.steps[indice],
                        status=StepStatus.SKIPPED,
                        duration=0.0,
                    )
                    for indice in posicoes
                )
                raise denied_decision(decisao)
            execute_with_policies(
                functools.partial(self._executar_passos, plan, runner, passos),
                context=contexto,
                timeout=timeout,
                recovery=recovery,
                governor=self._governor,
                sleeper=self._sleeper,
            )
            estado = ExecutionStatus.SUCCESS
            erro: WsaiError | None = None
        except CancellationError as problema:
            estado = ExecutionStatus.CANCELLED
            erro = problema
        except TimeoutError as problema:
            estado = ExecutionStatus.TIMEOUT
            erro = problema
        except WsaiError as problema:
            estado = ExecutionStatus.FAILED
            erro = problema
        except Exception as problema:  # noqa: BLE001 - normalizado para a taxonomia
            estado = ExecutionStatus.FAILED
            erro = _erro_wsai(problema)

        return ExecutionReport(
            execution_id=contexto.execution_id,
            task_id=plan.task_id,
            status=estado,
            steps=tuple(passos),
            duration=self._clock() - inicio,
            error=erro,
        )

    def _executar_passos(
        self,
        plan: ExecutionPlan,
        runner: StepRunner,
        registo: list[StepOutcome],
    ) -> None:
        """Executa os passos do plano, observando cada um no ``registo``.

        A lista ``registo`` é limpa em cada tentativa (compatível com a
        recuperação da unidade do plano) e, em caso de falha, o passo
        falhado fica registado antes de o erro ser re-lançado; os passos
        seguintes ficam ``SKIPPED``.
        """
        registo.clear()
        total = len(plan.steps)
        for indice, passo in enumerate(plan.steps):
            inicio = self._clock()
            try:
                runner(indice, passo)
            except Exception as problema:  # noqa: BLE001 - registado e propagado
                registo.append(
                    StepOutcome(
                        index=indice,
                        step=passo,
                        status=StepStatus.FAILED,
                        duration=self._clock() - inicio,
                        error=_erro_wsai(problema),
                    )
                )
                registo.extend(
                    StepOutcome(
                        index=posicao,
                        step=plan.steps[posicao],
                        status=StepStatus.SKIPPED,
                        duration=0.0,
                    )
                    for posicao in range(indice + 1, total)
                )
                raise
            registo.append(
                StepOutcome(
                    index=indice,
                    step=passo,
                    status=StepStatus.SUCCESS,
                    duration=self._clock() - inicio,
                )
            )


__all__ = ["RuntimeManager"]