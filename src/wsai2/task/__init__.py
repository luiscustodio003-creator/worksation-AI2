"""Subsistema Task Intelligence do WorkStation AI 2.

Responsável por definir e analisar o que o sistema tem de fazer —
tarefas, requisitos, capacidades e plano de execução (subsistema 3.7
da arquitectura).

Nesta unidade inicial é implementado o **contrato de tarefa**
(`TaskKind`, `Task`): a representação do pedido de trabalho, alinhada
com as categorias de modelo e independente de fornecedores. As unidades
seguintes classificam tarefas, mapeiam requisitos/capacidades e
constroem o plano de execução.
"""

from .base import Task, TaskKind

__all__ = ["Task", "TaskKind"]