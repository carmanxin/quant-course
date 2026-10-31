# @quantlab/output: cba199a9
import numpy as np

# 已有日收益率序列 returns 和原始夏普比率 original_sharpe
original_sharpe = returns.mean() / returns.std() * np.sqrt(252)

# Mean-Bootstrap：直接对收益率进行Bootstrap
n_boot = 2000
bootstrapped_sharpes = []
for _ in range(n_boot):
    boot_returns = np.random.choice(returns, size=len(returns), replace=True)
    boot_sharpe = boot_returns.mean() / boot_returns.std() * np.sqrt(252)
    bootstrapped_sharpes.append(boot_sharpe)

# 计算p值：Bootstrap夏普大于原始夏普的比例
p_value = np.mean(np.array(bootstrapped_sharpes) > original_sharpe)

# 置信区间
ci_lower = np.percentile(bootstrapped_sharpes, 2.5)
ci_upper = np.percentile(bootstrapped_sharpes, 97.5)

print(f"原始夏普比率: {original_sharpe:.2f}")
print(f"Bootstrap 95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")
print(f"p-value (H0: Sharpe <= 0, 保守): {p_value:.4f}")
