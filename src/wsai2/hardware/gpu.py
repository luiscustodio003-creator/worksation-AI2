"""Descoberta de GPU cross-platform (Windows/Linux).

Este módulo isola a lógica de obtenção de informação de GPUs,
suportando WMI no Windows e lspci/sysfs no Linux, com fallbacks
graciosos quando as ferramentas não estão disponíveis.
"""

from __future__ import annotations

import platform
import re
import subprocess
import sys
from typing import Optional

from .base import GpuInfo


_VENDOR_IDS = {
    "10de": "nvidia",
    "1002": "amd",
    "8086": "intel",
    "10ee": "xilinx",
    "13b5": "arm",
    "1a03": "asus",
    "1414": "microsoft",
}


def _normalize_vendor(vendor_str: str) -> str:
    """Normaliza string de vendor para identificador conhecido."""
    lowered = vendor_str.lower()
    for key, name in _VENDOR_IDS.items():
        if key in lowered or name in lowered:
            return name
    # Tentar extrair vendor conhecido do nome
    for name in ("nvidia", "amd", "intel", "arm", "qualcomm", "apple"):
        if name in lowered:
            return name
    return vendor_str.lower()[:32] if vendor_str else "unknown"


def _parse_vram_mb(vram_str: str) -> Optional[int]:
    """Converte string de VRAM para bytes."""
    try:
        # Formatos comuns: "8192 MB", "8 GB", "8192"
        vram_str = vram_str.upper().replace(",", "").strip()
        if "GB" in vram_str:
            gb = float(vram_str.replace("GB", "").strip())
            return int(gb * 1024 * 1024 * 1024)
        if "MB" in vram_str:
            mb = float(vram_str.replace("MB", "").strip())
            return int(mb * 1024 * 1024)
        # Assumir MB se for só número
        mb = float(vram_str)
        return int(mb * 1024 * 1024)
    except (ValueError, AttributeError):
        return None


def _discover_gpu_windows() -> list[GpuInfo]:
    """Descoberta de GPU no Windows via WMI."""
    gpus: list[GpuInfo] = []
    try:
        import wmi
        c = wmi.WMI()
        for gpu in c.Win32_VideoController():
            name = gpu.Name or "Unknown GPU"
            vram = None
            if gpu.AdapterRAM:
                vram = gpu.AdapterRAM
            driver_version = gpu.DriverVersion
            vendor = _normalize_vendor(name)
            gpus.append(GpuInfo(
                name=name.strip(),
                vendor=vendor,
                vram_bytes=vram,
                driver_version=driver_version,
            ))
    except Exception:
        # WMI não disponível ou erro
        pass
    return gpus


def _discover_gpu_linux() -> list[GpuInfo]:
    """Descoberta de GPU no Linux via lspci e sysfs."""
    gpus: list[GpuInfo] = []
    try:
        # lspci -nn para obter vendor:device IDs
        result = subprocess.run(
            ["lspci", "-nn", "-d", "::0300", "::0302", "::0380"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            # Tentar sem filtro de classe
            result = subprocess.run(
                ["lspci", "-nn"],
                capture_output=True, text=True, timeout=5
            )
        for line in result.stdout.splitlines():
            # Formato: "01:00.0 VGA compatible controller: NVIDIA Corporation GA102 [GeForce RTX 3080] [10de:2206]"
            match = re.search(r'\[([0-9a-f]{4}):([0-9a-f]{4})\]', line)
            if match:
                vendor_id, device_id = match.groups()
                vendor = _normalize_vendor(vendor_id)
                # Extrair nome após os dois pontos
                name_match = re.search(r':\s*(.+?)\s*\[', line)
                name = name_match.group(1).strip() if name_match else "Unknown GPU"
                # Tentar obter VRAM do sysfs
                vram = None
                try:
                    # Procurar em /sys/class/drm/
                    import os
                    for card in os.listdir("/sys/class/drm"):
                        if card.startswith("card"):
                            with open(f"/sys/class/drm/{card}/device/vendor", "r") as f:
                                sys_vendor = f.read().strip()
                            if sys_vendor == f"0x{vendor_id}":
                                # Tentar ler vram
                                vram_path = f"/sys/class/drm/{card}/device/mem_info_vram_total"
                                if os.path.exists(vram_path):
                                    with open(vram_path, "r") as f:
                                        vram = int(f.read().strip())
                                break
                except Exception:
                    pass
                # Driver version - tentar via glxinfo ou nvidia-smi
                driver = None
                try:
                    if vendor == "nvidia":
                        drv_result = subprocess.run(
                            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                            capture_output=True, text=True, timeout=3
                        )
                        if drv_result.returncode == 0:
                            driver = drv_result.stdout.strip().split("\n")[0]
                except Exception:
                    pass
                gpus.append(GpuInfo(
                    name=name,
                    vendor=vendor,
                    vram_bytes=vram,
                    driver_version=driver,
                ))
    except Exception:
        pass
    return gpus


def discover_gpus() -> list[GpuInfo]:
    """Descobre GPUs no sistema corrente."""
    system = platform.system().lower()
    if system == "windows":
        return _discover_gpu_windows()
    elif system == "linux":
        return _discover_gpu_linux()
    return []


__all__ = ["discover_gpus"]