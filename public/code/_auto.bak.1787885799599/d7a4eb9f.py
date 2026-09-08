# @quantlab/output: d7a4eb9f
def regime_based_factor_timing(factor_returns, regime_indicator):
    """
    基于市场状态（regime）的因子择时

    策略：在不同市场状态下使用不同的因子权重
    - 低波动/趋势市场：加大动量因子权重
    - 高波动/恐慌市场：加大质量和低波因子权重
    - 利率上升期：加大价值因子权重
    """
    # 定义不同状态下的因子权重
    regime_weights = {
        'trending': {'momentum': 0.4, 'value': 0.2, 'quality': 0.2, 'low_vol': 0.2},
        'volatile': {'momentum': 0.1, 'value': 0.1, 'quality': 0.4, 'low_vol': 0.4},
        'normal':   {'momentum': 0.25, 'value': 0.25, 'quality': 0.25, 'low_vol': 0.25},
    }

    dynamic_returns = []
    for date in factor_returns.index:
        regime = regime_indicator.get(date, 'normal')
        weights = regime_weights[regime]

        # 当日收益 = 各因子收益的加权平均
        daily_return = sum(
            factor_returns.loc[date, factor] * weight
            for factor, weight in weights.items()
        )
        dynamic_returns.append(daily_return)

    return pd.Series(dynamic_returns, index=factor_returns.index)
