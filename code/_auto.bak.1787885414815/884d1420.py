# @quantlab/output: 884d1420
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 计算信号和每日持仓
def moving_average_crossover(df, short_window=20, long_window=50):
    """
    双均线交叉策略
    """
    data = df.copy()

    # 计算均线
    data['MA_short'] = data['Close'].rolling(short_window).mean()
    data['MA_long'] = data['Close'].rolling(long_window).mean()

    # 生成信号：1为做多，-1为做空，0为无仓位
    data['Position'] = 0
    data.loc[data['MA_short'] > data['MA_long'], 'Position'] = 1
    data.loc[data['MA_short'] < data['MA_long'], 'Position'] = -1

    # 信号生成时考虑滞后（避免未来函数）
    data['Position'] = data['Position'].shift(1)
    data = data.dropna()

    # 计算策略收益率
    data['Market_Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Position'] * data['Market_Return']

    # 计算累计收益
    data['Cum_Market'] = (1 + data['Market_Return']).cumprod()
    data['Cum_Strategy'] = (1 + data['Strategy_Return']).cumprod()

    return data


# 使用示例 (需要一个包含 'Close' 列的 DataFrame)
# result = moving_average_crossover(df)
# result[['Cum_Market', 'Cum_Strategy']].plot(figsize=(12, 6))
# plt.show()

# 绩效统计函数
def performance_stats(returns, trading_days=252):
    """计算策略绩效指标"""
    annual_return = returns.mean() * trading_days
    annual_vol = returns.std() * np.sqrt(trading_days)
    sharpe = annual_return / annual_vol
    cum_returns = (1 + returns).cumprod()
    max_drawdown = (cum_returns / cum_returns.cummax() - 1).min()
    win_rate = (returns > 0).mean()

    return {
        '年化收益率': f'{annual_return:.2%}',
        '年化波动率': f'{annual_vol:.2%}',
        '夏普比率': f'{sharpe:.2f}',
        '最大回撤': f'{max_drawdown:.2%}',
        '胜率': f'{win_rate:.2%}'
    }

# print(performance_stats(result['Strategy_Return'].dropna()))
