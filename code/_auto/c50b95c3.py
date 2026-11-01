# @quantlab/output: c50b95c3
def volatility_risk_premium_strategy(vix_spot: float,
                                      vix_futures_curve: np.ndarray,
                                      vix_call_prices: np.ndarray,
                                      portfolio_beta: float = 1.0) -> dict:
    """
    基于波动率风险溢价（VRP）的尾部对冲策略。

    VRP = 隐含波动率 - 已实现波动率，通常为正。

    策略：在 VIX 低位时买入 VIX Call（保险便宜），
          在 VIX 高位时卖出（保险贵）。

    参数:
        vix_spot: 当前 VIX 水平
        vix_futures_curve: VIX 期货曲线
        vix_call_prices: 不同行权价的 VIX Call 价格
        portfolio_beta: 组合对市场的敏感度
    返回:
        对冲信号
    """
    # VIX 分位数判断
    vix_percentile = norm.cdf(
        (vix_spot - 20) / 8
    )  # 假设 VIX 均值 20，标准差 8

    # 期货升贴水判断
    contango = vix_futures_curve[0] - vix_spot

    # 信号逻辑
    if vix_percentile < 0.3 and contango > 0:
        # VIX 低位 + 升水：买入对冲的时机（保险便宜）
        hedge_action = 'BUY_TAIL_HEDGE'
        target_allocation = 0.03  # 3% 组合价值
    elif vix_percentile > 0.8:
        # VIX 高位：减少对冲或获利了结
        hedge_action = 'REDUCE_HEDGE'
        target_allocation = 0.01
    else:
        hedge_action = 'HOLD'
        target_allocation = 0.02

    # 对冲比率（考虑组合 beta）
    adjusted_allocation = target_allocation * max(portfolio_beta, 0.5)

    return {
        'VIX_Spot': vix_spot,
        'VIX_Percentile': vix_percentile * 100,
        'VIX_Contango': contango,
        'Hedge_Action': hedge_action,
        'Target_Hedge_Allocation': adjusted_allocation * 100,
        'Signal_Strength': abs(vix_percentile - 0.5) * 2
    }
