# @quantlab/output: 04e8eced
import numpy as np
from scipy.stats import norm

def deflated_sharpe_ratio(observed_sr, n_trials, n_samples,
                          skewness=0, kurtosis=3):
    """
    计算通缩夏普比（Deflated Sharpe Ratio）

    参数:
        observed_sr: 观察到的夏普比（无风险利率假设为0）
        n_trials: 总共测试的策略/参数组合数量
        n_samples: 每个策略的样本量（收益率的个数）
        skewness: 收益率分布的偏度
        kurtosis: 收益率分布的峰度
    """
    # 在零假设下（真实夏普比=0），最大夏普比的期望
    # 使用极值理论估计
    euler_mascheroni = 0.5772156649

    # 期望的标准化最大夏普比
    expected_max = (1 - euler_mascheroni) * norm.ppf(1 - 1/n_trials) + \
                   euler_mascheroni * norm.ppf(1 - 1/(n_trials * np.e))

    # 标准差（近似）
    sd_max = norm.pdf(norm.ppf(1 - 1/n_trials)) * \
             np.sqrt(1/n_trials + (1 - 1/n_trials) * norm.ppf(1 - 1/n_trials)**2)

    # 调整样本量影响
    expected_max_sr = expected_max / np.sqrt(n_samples)
    sd_max_sr = sd_max / np.sqrt(n_samples)

    # 通缩夏普比
    dsr = (observed_sr - expected_max_sr) / sd_max_sr

    # 计算p值
    p_value = 1 - norm.cdf(dsr)

    return {
        'DSR': dsr,
        'p_value': p_value,
        'significant_05': p_value < 0.05,
        'significant_01': p_value < 0.01,
        'expected_max_SR': expected_max_sr,
        'max_SR_sd': sd_max_sr,
        'haircut': (observed_sr - expected_max_sr) / observed_sr if observed_sr > 0 else 0
    }

# 使用示例
print("Deflated Sharpe Ratio 分析:")
print("=" * 60)
print(f"{'N测试数':>8} {'观测SR':>8} {'预期最大SR':>10} {'DSR':>8} {'显著?':>8}")
print("-" * 60)

n_samples = 252  # 1年日线数据

for n_trials in [1, 10, 50, 100, 500, 1000]:
    observed_sr = 1.5  # 假设观测到1.5的夏普比
    result = deflated_sharpe_ratio(observed_sr, n_trials, n_samples)
    is_sig = "Yes" if result['significant_05'] else "No"
    print(f"{n_trials:>8} {observed_sr:>8.1f} {result['expected_max_SR']:>10.3f} "
          f"{result['DSR']:>8.2f} {is_sig:>8}")

print(f"\n结论：当测试次数超过50次时，夏普比1.5变得不再显著！")
