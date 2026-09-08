# @quantlab/output: 00325c46
def multi_asset_trend_following(prices_dict, lookback=252):
    """
    多品种趋势跟踪：对每个品种独立计算趋势信号
    最终组合为各品种的等权组合

    Parameters:
        prices_dict: dict, {asset_name: pd.Series of prices}
    """
    signals = {}
    returns = {}

    for asset, price in prices_dict.items():
        # 时间序列动量信号：基于过去N日收益的方向
        momentum = price.pct_change(lookback).dropna()

        # 信号：做多正动量，做空负动量
        signal = pd.Series(np.sign(momentum), index=momentum.index)

        # 日收益（扣除前移一期信号，避免前视偏差）
        daily_ret = price.pct_change()
        strategy_ret = signal.shift(1) * daily_ret

        signals[asset] = signal
        returns[asset] = strategy_ret

    # 组合收益：各品种等权
    returns_df = pd.DataFrame(returns)
    portfolio_returns = returns_df.mean(axis=1)

    # 年化波动率目标（如15%），调整杠杆
    current_vol = portfolio_returns.std() * np.sqrt(252)
    target_vol = 0.15
    scaled_returns = portfolio_returns * (target_vol / current_vol)

    return scaled_returns, signals
