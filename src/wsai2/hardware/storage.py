"""Descoberta de armazenamento cross-platform (Windows/Linux).

Este módulo usa psutil para obter partições e informação de discos,
normalizando para os contratos definidos em base.py.
"""

from __future__ import annotations

import psutil

from .base import StorageInfo


def _normalize_disk_type(device: str, opts: str) -> str:
    """Tenta inferir tipo de disco (SSD, HDD, NVMe)."""
    device_lower = device.lower()
    opts_lower = opts.lower()
    # Heurísticas comuns
    if "nvme" in device_lower:
        return "nvme"
    if "ssd" in opts_lower or "solid" in opts_lower:
        return "ssd"
    if "removable" in opts_lower or "usb" in device_lower:
        return "usb"
    # No Linux, tentar /sys/block/.../queue/rotational
    try:
        import os
        # Extrair nome do disco base (ex: /dev/sda1 -> sda)
        import re
        match = re.search(r'([a-z]+)\d*$', device_lower)
        if match:
            disk_name = match.group(1)
            rotational_path = f"/sys/block/{disk_name}/queue/rotational"
            if os.path.exists(rotational_path):
                with open(rotational_path, "r") as f:
                    if f.read().strip() == "0":
                        return "ssd"
                    return "hdd"
    except Exception:
        pass
    return "unknown"


def discover_storage() -> list[StorageInfo]:
    """Descobre dispositivos de armazenamento montados."""
    storage: list[StorageInfo] = []
    try:
        partitions = psutil.disk_partitions(all=False)
        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                dtype = _normalize_disk_type(part.device, part.opts)
                storage.append(StorageInfo(
                    device_path=part.device,
                    total_bytes=usage.total,
                    type=dtype,
                    mount_point=part.mountpoint,
                ))
            except (PermissionError, OSError):
                # Partição não acessível (ex: CD-ROM vazio, partição de recovery)
                continue
    except Exception:
        pass
    return storage


__all__ = ["discover_storage"]