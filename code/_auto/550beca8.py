# @quantlab/output: 550beca8
import numpy as np


def fair_coin_from_biased(p: float = 0.7, n_samples: int = 10000) -> dict:
    """
    Von Neumann 算法：用正面概率为 p 的偏心硬币产出公平的 0/1

    Parameters
    ----------
    p : float
        不公平硬币的正面概率
    n_samples : int
        需要产出的公平样本数

    Returns
    -------
    dict: mean（公平样本均值）、tosses（总投掷次数）、
          tosses_per_bit（每产出 1 bit 的平均投掷次数）
    """
    fair_results = []
    tosses = 0

    while len(fair_results) < n_samples:
        toss1 = np.random.random() < p
        toss2 = np.random.random() < p
        tosses += 2

        if toss1 and not toss2:      # (正, 反) → 输出 1
            fair_results.append(1)
        elif not toss1 and toss2:    # (反, 正) → 输出 0
            fair_results.append(0)
        # (正,正) / (反,反) → 丢弃重掷

    return {
        'mean': float(np.mean(fair_results)),
        'tosses': tosses,
        'tosses_per_bit': tosses / n_samples,
    }


np.random.seed(42)

# 1) 重复 1000 轮，检验均值是否无偏
means = [fair_coin_from_biased(p=0.7, n_samples=500)['mean'] for _ in range(1000)]
print(f"p=0.70，每轮 500 个公平样本，重复 1000 轮:")
print(f"  均值的均值: {np.mean(means):.4f}   (理论 0.5)")
print(f"  均值的标准差: {np.std(means):.4f}  (理论 0.5/√500 = {0.5 / np.sqrt(500):.4f})")

# 2) 效率随偏心程度的变化：接受概率 2p(1-p)，每 bit 期望投掷 1/(p(1-p))
print(f"\n{'p':>6}{'实测均值':>12}{'实测投掷/bit':>16}{'理论 1/(p(1-p))':>18}")
print("-" * 54)
for p in [0.5, 0.6, 0.7, 0.9, 0.99]:
    r = fair_coin_from_biased(p=p, n_samples=4000)
    print(f"{p:>6.2f}{r['mean']:>12.4f}{r['tosses_per_bit']:>16.2f}"
          f"{1 / (p * (1 - p)):>18.2f}")

print("\n结论：无论 p 多偏，输出都严格是 50/50（无偏性与 p 无关）；")
print("      但代价是效率——p 越极端，期望投掷次数 1/(p(1-p)) 越高，p=0.99 时约需 101 次/bit。")
