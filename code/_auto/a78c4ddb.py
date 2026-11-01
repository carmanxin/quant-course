# @quantlab/output: a78c4ddb
import random


def prisoner_strategy(permutation: list[int], prisoner: int, limit: int) -> bool:
    box = prisoner
    for _ in range(limit):
        card = permutation[box]
        if card == prisoner:
            return True
        box = card
    return False


def estimate_group_success(n: int = 100, limit: int = 50, trials: int = 5_000) -> float:
    rng = random.Random(7)
    success = 0
    for _ in range(trials):
        permutation = list(range(n))
        rng.shuffle(permutation)
        success += all(prisoner_strategy(permutation, p, limit) for p in range(n))
    return success / trials


print(f"全员成功率约为 {estimate_group_success():.1%}")
