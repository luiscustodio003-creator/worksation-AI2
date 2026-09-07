"""Descoberta de CPU usando psutil com normalização cross-platform.

Este módulo isola a lógica de obtenção de informação do processador,
normalizando os dados brutos do psutil para os contratos definidos em
``base.py``.
"""

from __future__ import annotations

import platform
import re

import psutil

from .base import Architecture, CpuInfo, CpuVendor


_VENDOR_PATTERNS = {
    CpuVendor.INTEL: (r"intel", r"genuineintel"),
    CpuVendor.AMD: (r"amd", r"authentica(?:md)?"),
    CpuVendor.ARM: (r"arm",),
    CpuVendor.QUALCOMM: (r"qualcomm",),
    CpuVendor.APPLE: (r"apple",),
}


def _normalize_vendor(raw_vendor: str) -> CpuVendor:
    """Normaliza o identificador bruto do fabricante para CpuVendor."""
    lowered = raw_vendor.lower()
    for vendor, patterns in _VENDOR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                return vendor
    return CpuVendor.UNKNOWN


def _normalize_architecture(raw_arch: str) -> Architecture:
    """Normaliza a arquitectura bruta para Architecture."""
    lowered = raw_arch.lower()
    if lowered in ("x86_64", "amd64", "x64"):
        return Architecture.X86_64
    if lowered in ("arm64", "aarch64"):
        return Architecture.ARM64
    if lowered in ("arm", "armv7l", "armv8l"):
        return Architecture.ARM
    if lowered in ("x86", "i386", "i686"):
        return Architecture.X86
    return Architecture.UNKNOWN


def _extract_cpu_features() -> tuple[str, ...]:
    """Extrai flags de funcionalidades do CPU (Linux: /proc/cpuinfo, Windows: psutil)."""
    features: list[str] = []
    try:
        # psutil expõe cpu_freq mas não flags diretamente
        # Em Linux, podemos ler /proc/cpuinfo
        import os
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
                # Procurar a linha 'flags' da primeira CPU
                for line in content.splitlines():
                    if line.startswith("flags"):
                        flags_str = line.split(":", 1)[1].strip()
                        features = flags_str.split()
                        break
    except Exception:
        pass
    return tuple(features)


def discover_cpu() -> CpuInfo:
    """Descobre e devolve a informação normalizada do CPU."""
    # Informação base do psutil
    physical_cores = psutil.cpu_count(logical=False) or 1
    logical_cores = psutil.cpu_count(logical=True) or 1

    # Frequência máxima (pode não estar disponível em todos os SO)
    max_freq = None
    try:
        freq = psutil.cpu_freq()
        if freq and freq.max:
            max_freq = freq.max
    except Exception:
        pass

    # Cache info — psutil não expõe directamente, tentar heurísticas
    cache_l1 = cache_l2 = cache_l3 = None

    # Vendor e model name
    raw_vendor = "unknown"
    model_name = platform.processor() or "Unknown CPU"

    # Tentar obter vendor via psutil (Linux) ou platform (Windows)
    try:
        import os
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("vendor_id"):
                        raw_vendor = line.split(":", 1)[1].strip()
                        break
                    elif line.startswith("model name") and model_name == "Unknown CPU":
                        model_name = line.split(":", 1)[1].strip()
    except Exception:
        pass

    # Em Windows, platform.processor() costuma dar o nome; tentar psutil
    if raw_vendor == "unknown":
        try:
            # psutil 5.9+ tem cpu_info() em algumas plataformas
            cpu_info = psutil.cpu_info()
            if hasattr(cpu_info, "vendor"):
                raw_vendor = cpu_info.vendor
            if hasattr(cpu_info, "brand"):
                model_name = cpu_info.brand
        except Exception:
            pass

    vendor = _normalize_vendor(raw_vendor)
    arch = _normalize_architecture(platform.machine())
    features = _extract_cpu_features()

    return CpuInfo(
        vendor=vendor,
        model_name=model_name,
        architecture=arch,
        physical_cores=physical_cores,
        logical_cores=logical_cores,
        max_frequency_mhz=max_freq,
        cache_l1_kb=cache_l1,
        cache_l2_kb=cache_l2,
        cache_l3_kb=cache_l3,
        features=features,
    )


__all__ = ["discover_cpu"]