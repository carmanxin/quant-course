# @quantlab/output: 5.3-stat-arb
import numpy as np
np.random.seed(42)
n = 200
stock1 = 100 + np.cumsum(np.random.randn(n) * 0.5)
stock2 = stock1 * 0.8 + np.random.randn(n) * 2
hedge_ratio = np.polyfit(stock1, stock2, 1)[0]
spread = stock2 - hedge_ratio * stock1
zscore = (spread - np.mean(spread)) / np.std(spread)
print(f'对冲比率: {hedge_ratio:.3f}')
print(f'最新价差 z-score: {zscore[-1]:.2f}')
if zscore[-1] > 2:
    print('信号: 做多 stock1 + 做空 stock2（价差过高，预期回归）')
elif zscore[-1] < -2:
    print('信号: 做空 stock1 + 做多 stock2（价差过低，预期回归）')
else:
    print('信号: 不交易（价差在正常范围）')
