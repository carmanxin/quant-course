# @quantlab/output: 30e7b4f9
import numpy as np

# 广播：计算所有股票相对于各自均值的偏离
returns = np.random.randn(1000, 500)  # 1000天, 500只股票
stock_means = returns.mean(axis=0)    # shape (500,)
demeaned = returns - stock_means      # (1000, 500) - (500,) -> (1000, 500) 自动广播

# 花式索引：筛选满足条件的行
high_vol_days = returns[np.abs(returns.mean(axis=1)) > 0.02]
