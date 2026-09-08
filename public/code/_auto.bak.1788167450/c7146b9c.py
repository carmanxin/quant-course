# @quantlab/output: c7146b9c
from __future__ import annotations


def amdahl_speedup(serial_fraction: float, threads: int) -> float:
    if not 0.0 <= serial_fraction <= 1.0:
        raise ValueError("serial_fraction 必须在 0 到 1 之间")
    if threads < 1:
        raise ValueError("threads 必须为正整数")
    return 1.0 / (serial_fraction + (1.0 - serial_fraction) / threads)


for n in [1, 2, 4, 8, 16, 30, 32, 64]:
    print(f"threads={n:>2}, speedup={amdahl_speedup(0.08, n):.2f}x")
