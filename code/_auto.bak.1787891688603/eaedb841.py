# @quantlab/output: eaedb841
# vectorbt 加速
import vectorbt as vbt
import numpy as np

# 1. Numba JIT 缓存(重复跑时省编译时间)
vbt.settings.numba['cache'] = True
vbt.settings.numba['parallel'] = True  # 多核并行

# 2. 用 Numba 直接写最热循环
from numba import njit

@njit
def fast_sma(prices: np.ndarray, window: int) -> np.ndarray:
    """比 pd.Series.rolling 快 5-10 倍"""
    n = len(prices)
    out = np.full(n, np.nan)
    if n < window:
        return out
    cumsum = np.cumsum(prices)
    for i in range(window - 1, n):
        out[i] = (cumsum[i] - cumsum[i - window + 1] + prices[i - window]) / window
    return out

# 3. 用 Numba parallel 多核并行跑多组参数
@njit(parallel=True)
def grid_search(prices: np.ndarray, short_grid: np.ndarray, long_grid: np.ndarray):
    n = len(short_grid) * len(long_grid)
    results = np.empty(n)
    idx = 0
    for i in nb.prange(short_grid.shape[0]):
        for j in nb.prange(long_grid.shape[0]):
            # 计算夏普...
            results[idx] = sharpe
            idx += 1
    return results
