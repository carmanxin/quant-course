import numpy as np
np.random.seed(42)
returns = np.random.randn(500) * 0.012 + 0.0004
nav = np.cumprod(1 + returns)
mean_daily = np.mean(returns)
std_daily = np.std(returns)
ann_ret = mean_daily * 252
ann_vol = std_daily * np.sqrt(252)
sharpe = ann_ret / ann_vol
peak = np.maximum.accumulate(nav)
drawdown = (nav - peak) / peak
max_dd = drawdown.min()
calmar = ann_ret / abs(max_dd)
print(f'年化收益率: {ann_ret*100:.2f}%')
print(f'年化波动率: {ann_vol*100:.2f}%')
print(f'夏普比率: {sharpe:.2f}')
print(f'最大回撤: {max_dd*100:.2f}%')
print(f'卡玛比率: {calmar:.2f}')
