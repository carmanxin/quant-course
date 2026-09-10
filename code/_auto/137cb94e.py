# @quantlab/output: 137cb94e
import numpy as np
import pandas as pd
import vectorbt as vbt

# 1. 准备价格数据(A股示例:用随机游走模拟一只股票)
np.random.seed(42)
n_days = 1000
dates = pd.bdate_range('2022-01-01', periods=n_days)  # 仅工作日
close = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, n_days)))
df = pd.DataFrame({'close': close}, index=dates)

# 2. 构造双均线信号(短均线上穿长均线 → 买入)
short_ma = vbt.MA.run(df['close'], window=10)
long_ma = vbt.MA.run(df['close'], window=50)
entries = short_ma.ma_crossed_above(long_ma)
exits = short_ma.ma_crossed_below(long_ma)

# 3. 一行回测(向量化!快到极致)
pf = vbt.Portfolio.from_signals(
    close=df['close'],
    entries=entries,
    exits=exits,
    init_cash=1_000_000,
    fees=0.0003,       # 万三佣金
    slippage=0.001,    # 千一滑点
    freq='1D'
)

# 4. 查看绩效
print(pf.stats())
# 输出:Total Return, Sharpe Ratio, Max Drawdown, Win Rate...
print(f"\n总收益: {pf.total_return():.2%}")
print(f"夏普比率: {pf.sharpe_ratio():.2f}")
print(f"最大回撤: {pf.max_drawdown():.2%}")
