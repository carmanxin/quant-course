# @quantlab/output: b280c4f1
from __future__ import annotations

import random
from collections import Counter


def monty_hall(n_trials: int = 100_000, seed: int = 42) -> dict[str, float]:
    """在主持人知情且必开羊门的规则下比较坚持与换门。"""
    rng = random.Random(seed)
    wins = Counter()

    for _ in range(n_trials):
        prize = rng.randrange(3)
        first = rng.randrange(3)
        host_choices = [d for d in range(3) if d != first and d != prize]
        opened = rng.choice(host_choices)
        switched = next(d for d in range(3) if d not in {first, opened})
        wins["stay"] += first == prize
        wins["switch"] += switched == prize

    return {name: count / n_trials for name, count in wins.items()}


print(monty_hall())
