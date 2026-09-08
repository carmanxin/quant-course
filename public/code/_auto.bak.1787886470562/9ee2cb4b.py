# @quantlab/output: 9ee2cb4b
import numpy as np
from scipy import stats

def demonstrate_multiple_testing(n_factors=100, n_obs=504, true_alpha_fraction=0.05):
    """
    演示多重假设检验问题

    在n_factors中，只有 true_alpha_fraction 比例是真正有效的因子
    """
    n_true = int(n_factors * true_alpha_fraction)

    # 生成收益率数据
    returns = np.random.randn(n_obs) * 0.02  # 基础噪声

    p_values = []
    is_true = []

    for i in range(n_factors):
        if i < n_true:
            # 真正有效的因子
            factor = returns * 0.5 + np.random.randn(n_obs) * 0.02  # 与收益有一定相关性
            is_true.append(True)
        else:
            # 纯噪声因子
            factor = np.random.randn(n_obs) * 0.02
            is_true.append(False)

        _, p_value = stats.pearsonr(returns, factor)
        p_values.append(p_value)

    p_values = np.array(p_values)
    is_true = np.array(is_true)

    # 不同校正方法
    n_tests = len(p_values)

    # 1. 无校正（naive，α=0.05）
    naive_selected = p_values < 0.05

    # 2. Bonferroni校正
    bonf_threshold = 0.05 / n_tests
    bonf_selected = p_values < bonf_threshold

    # 3. Benjamini-Hochberg FDR控制
    sorted_indices = np.argsort(p_values)
    bh_threshold = None
    for k, idx in enumerate(sorted_indices):
        if p_values[idx] <= (k + 1) / n_tests * 0.05:
            bh_threshold = p_values[idx]
    bh_selected = p_values <= bh_threshold if bh_threshold else np.zeros(n_tests, dtype=bool)

    # 报告结果
    print(f"总因子数: {n_factors}, 真实有效因子数: {n_true}")
    print(f"\n{'方法':<25} {'选中数':>8} {'真阳性':>8} {'假阳性':>8} {'FDR':>8}")
    print("-" * 60)

    for name, selected in [('Naive (α=0.05)', naive_selected),
                            ('Bonferroni', bonf_selected),
                            ('BH FDR', bh_selected)]:
        true_positive = np.sum(selected & is_true)
        false_positive = np.sum(selected & ~is_true)
        fdr = false_positive / max(np.sum(selected), 1)
        print(f"{name:<25} {np.sum(selected):>8} {true_positive:>8} "
              f"{false_positive:>8} {fdr:>8.1%}")

demonstrate_multiple_testing(n_factors=100, n_obs=504, true_alpha_fraction=0.05)
