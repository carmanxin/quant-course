# @quantlab/output: 5141c4d0
def fair_coin_from_biased(p: float = 0.7, n_samples: int = 10000) -> float:
    """
    从不公平硬币生成公平结果

    Parameters
    ----------
    p : float
        不公平硬币的正面概率
    n_samples : int
        模拟的样本数
    """
    fair_results = []

    while len(fair_results) < n_samples:
        # 连续掷两次
        toss1 = np.random.random() < p
        toss2 = np.random.random() < p

        if toss1 and not toss2:  # (正, 反)
            fair_results.append(1)  # "正面"
        elif not toss1 and toss2:  # (反, 正)
            fair_results.append(0)  # "反面"
        # 否则重新掷

    return np.mean(fair_results)


# 验证
from collections import Counter
np.random.seed(42)
results = []
for _ in range(1000):
    results.append(fair_coin_from_biased(p=0.7, n_samples=500).mean())

print(f"公平硬币的均值: {np.mean(results):.4f} (期望 0.5)")
print(f"标准差: {np.std(results):.4f}")
