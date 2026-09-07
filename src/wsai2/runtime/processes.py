"""Descoberta de processos activos usando psutil cross-platform.

Este módulo isola a lógica de obtenção de informação sobre processos,
providenciando uma visão resumida dos mais relevantes em termos de
utilização de recursos. Representa *Runtime State*.
"""

from __future__ import annotations

import psutil

from .base import ProcessInfo


def _normalize_status(raw: str) -> str:
    """Normaliza o estado do processo para valor legível."""
    mapping = {
        psutil.STATUS_RUNNING: "running",
        psutil.STATUS_SLEEPING: "sleeping",
        psutil.STATUS_DISK_SLEEP: "disk_sleep",
        psutil.STATUS_STOPPED: "stopped",
        psutil.STATUS_TRACING_STOP: "tracing_stop",
        psutil.STATUS_ZOMBIE: "zombie",
        psutil.STATUS_DEAD: "dead",
        psutil.STATUS_IDLE: "idle",
        psutil.STATUS_WAITING: "waiting",
    }
    return mapping.get(raw, raw or "unknown")


def discover_top_processes(limit: int = 10) -> tuple[ProcessInfo, ...]:
    """Descobre os processos que mais consomem memória.

    Args:
        limit: número máximo de processos a devolver (mínimo 1).

    Devolve uma tupla de :class:`ProcessInfo` ordenada por utilização
    de memória RSS (decrescente).
    """
    limit = max(1, limit)
    procs: list[ProcessInfo] = []

    try:
        # Iterar processos — psutil.process_iter é cross-platform
        for proc in psutil.process_iter(
            attrs=["pid", "name", "status", "cpu_percent", "memory_info", "memory_percent"],
            ad_value=None,
        ):
            try:
                info = proc.info
                if info["memory_info"] is None:
                    continue

                status = _normalize_status(info["status"] or "")
                cpu_pct = float(info["cpu_percent"] or 0.0)
                rss = int(info["memory_info"].rss)
                mem_pct = float(info["memory_percent"] or 0.0)

                procs.append(ProcessInfo(
                    pid=info["pid"],
                    name=str(info["name"] or "unknown"),
                    status=status,
                    cpu_percent=cpu_pct,
                    memory_rss_bytes=rss,
                    memory_percent=mem_pct,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception:
        pass

    # Ordenar por memória RSS (decrescente) e limitar
    procs.sort(key=lambda p: p.memory_rss_bytes, reverse=True)
    return tuple(procs[:limit])


__all__ = ["discover_top_processes"]
