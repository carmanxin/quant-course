import numpy as np
returns = np.random.randn(500) * 0.01 + 0.0005
original_sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
# H0: Sharpe=0 → 将收益率中心化消除样本均值
centered = returns - np.mean(returns)
bootstrapped = [np.mean(np.random.choice(centered, size=500)) / np.std(np.random.choice(centered, size=500)) * np.sqrt(252) for _ in range(1000)]
p_value = np.mean(np.array(bootstrapped) >= original_sharpe)
print(f'原始夏普比率: {original_sharpe:.3f}')
print(f'Bootstrap p值: {p_value:.3f}')
