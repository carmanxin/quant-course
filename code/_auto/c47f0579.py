# @quantlab/output: c47f0579
from functools import lru_cache


def expected_rolls_to_target(target: int = 6) -> float:
    """公平六面骰掷到目标点数的期望次数。"""
    p = 1.0 / 6.0
    # E = 1 + (1-p)E，因此 E = 1/p。
    return 1.0 / p


@lru_cache(maxsize=None)
def expected_steps(distance: int) -> float:
    """每次等概率前进 1 或 2 格，越过终点也算完成。"""
    if distance <= 0:
        return 0.0
    return 1.0 + 0.5 * expected_steps(distance - 1) + 0.5 * expected_steps(distance - 2)


print(expected_rolls_to_target())
print(round(expected_steps(10), 4))
