# @quantlab/output: 95b4d880
import pandas as pd
import numpy as np

def dual_ma_strategy(df, short_window=20, long_window=50):
    """
    双均线策略回测

    Parameters:
        df: DataFrame with 'Close' column
        short_window: 短期均线周期（默认20日）
        long_window: 长期均线周期（默认50日）
    Returns:
        DataFrame with added columns: SMA_short, SMA_long, signal, position, returns
    """
    data = df.copy()

    # 计算均线
    data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_long'] = data['Close'].rolling(window=long_window).mean()

    # 生成信号：短均线在长均线之上为1（看多），之下为0（看空/空仓）
    data['signal'] = np.where(data['SMA_short'] > data['SMA_long'], 1, 0)

    # 仓位：用信号的变化（交叉点）来触发交易
    data['position'] = data['signal'].shift(1)  # 下一期才执行

    # 计算收益率
    data['market_returns'] = data['Close'].pct_change()
    data['strategy_returns'] = data['position'] * data['market_returns']

    # 累积收益
    data['cumulative_market'] = (1 + data['market_returns']).cumprod()
    data['cumulative_strategy'] = (1 + data['strategy_returns']).cumprod()

    return data
