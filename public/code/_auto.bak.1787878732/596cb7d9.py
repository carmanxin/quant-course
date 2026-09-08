# @quantlab/output: 596cb7d9
def global_macro_momentum(asset_prices: pd.DataFrame,
                           n_assets: int = 10,
                           momentum_months: int = 6,
                           rebalance_freq: str = 'M') -> pd.DataFrame:
    """
    全球宏观动量策略：做多过去N个月表现最好的资产。

    参数:
        asset_prices: 全球资产价格矩阵
            (含股票指数、债券指数、商品、外汇)
        n_assets: 做多资产数量
        momentum_months: 动量回看月数
        rebalance_freq: 调仓频率 ('M'=每月)
    返回:
        策略权重和收益
    """
    # 计算动量信号
    momentum_signal = asset_prices.pct_change(momentum_months * 21)

    # 每月调仓
    weights = pd.DataFrame(0.0, index=asset_prices.index,
                           columns=asset_prices.columns)

    if rebalance_freq == 'M':
        rebalance_dates = asset_prices.resample('M').last().index

        for date in rebalance_dates:
            if date in momentum_signal.index:
                mom = momentum_signal.loc[date]
                top_assets = mom.nlargest(n_assets).index

                # 等权配置
                weight_value = 1.0 / n_assets
                weights.loc[date:, top_assets] = weight_value

    # 策略收益
    asset_returns = asset_prices.pct_change()
    strategy_returns = (weights.shift(1) * asset_returns).sum(axis=1)

    return strategy_returns
