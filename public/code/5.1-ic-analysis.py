import numpy as np
from scipy.stats import spearmanr
np.random.seed(42)
n_periods, n_stocks = 50, 100
ic_series = []
for t in range(n_periods):
    factor = np.random.randn(n_stocks) * 0.1
    fwd_return = 0.02 * factor + np.random.randn(n_stocks) * 0.05
    ic, _ = spearmanr(factor, fwd_return)
    ic_series.append(ic)
ic_mean = np.mean(ic_series)
ic_std = np.std(ic_series)
ir = ic_mean / ic_std if ic_std > 0 else 0
print(f'IC 均值: {ic_mean:.4f}')
print(f'IC 标准差: {ic_std:.4f}')
print(f'IR (信息比率): {ir:.2f}')
