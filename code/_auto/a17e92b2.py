# @quantlab/output: a17e92b2
import numpy as np
import pandas as pd

np.random.seed(42)

# 模拟 252 天的 50ETF 收盘价
n_days = 252
daily_vol = 0.014
returns = np.random.randn(n_days) * daily_vol
prices = 2.800 * np.exp(np.cumsum(returns))
log_returns = np.log(prices[1:] / prices[:-1])

print(f"数据集: {n_days} 天, 年化 vol ≈ {log_returns.std()*np.sqrt(252)*100:.2f}%")
