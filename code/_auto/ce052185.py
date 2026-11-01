# @quantlab/output: ce052185
def cross_exchange_stat_arb(exchange_prices, lookback_hours=24):
    """
    跨所永续合约统计套利框架
    exchange_prices: dict {exchange: pd.Series of minute prices}
    """
    import pandas as pd
    prices_df = pd.DataFrame(exchange_prices)

    # 计算跨所价差
    # 以中位数价格为基准
    median_price = prices_df.median(axis=1)
    deviations = prices_df.sub(median_price, axis=0)

    # 滚动统计：每个交易所的价格偏离度
    rolling_mean = deviations.rolling(f'{lookback_hours}h').mean()
    rolling_std = deviations.rolling(f'{lookback_hours}h').std()

    z_scores = (deviations - rolling_mean) / rolling_std

    # 生成交易信号
    signals = pd.DataFrame(index=prices_df.index, columns=prices_df.columns)
    for col in prices_df.columns:
        signals[col] = 0
        signals.loc[z_scores[col] > 2.0, col] = -1  # 价格偏高 → 做空
        signals.loc[z_scores[col] < -2.0, col] = 1   # 价格偏低 → 做多

    return {
        'prices': prices_df,
        'deviations': deviations,
        'z_scores': z_scores,
        'signals': signals
    }
