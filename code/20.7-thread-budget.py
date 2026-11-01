# @quantlab/output: 20.7-thread-budget
from __future__ import annotations


def amdahl_speedup(serial_fraction: float, threads: int) -> float:
    """Amdahl 定律下的理论加速比。"""
    return 1.0 / (serial_fraction + (1.0 - serial_fraction) / threads)


def thread_budget(
    physical_cores: int,
    serial_fraction: float,
    reserved_cores: int = 2,
    max_threads: int | None = None,
) -> list[tuple[int, float, float]]:
    """输出候选线程数、理论加速比和新增一线程的边际收益。"""
    usable = max(1, physical_cores - reserved_cores)
    upper = max_threads or usable * 2
    rows = []
    previous = amdahl_speedup(serial_fraction, 1)
    for threads in range(1, upper + 1):
        speedup = amdahl_speedup(serial_fraction, threads)
        marginal = speedup - previous if threads > 1 else speedup
        rows.append((threads, speedup, marginal))
        previous = speedup
    return rows


rows = thread_budget(physical_cores=32, serial_fraction=0.08)
print("线程数  理论加速比  新增线程边际收益")
for threads, speedup, marginal in rows:
    if threads in {1, 2, 4, 8, 16, 24, 30, 32, 48, 60}:
        print(f"{threads:>6}  {speedup:>10.2f}  {marginal:>16.4f}")

print("\n结论：先保留行情、OS 和风控所需核心，再用基准测试决定线程数。")
