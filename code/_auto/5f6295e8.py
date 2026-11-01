# @quantlab/output: 5f6295e8
def tail_hedge_cost_benefit(portfolio_returns: np.ndarray,
                             hedged_returns: np.ndarray,
                             annual_premium_bps: float) -> dict:
    """
    评估尾部对冲的成本效益。

    参数:
        portfolio_returns: 未对冲的组合日收益率
        hedged_returns: 对冲后的组合日收益率（已扣除成本）
        annual_premium_bps: 年化对冲成本（基点）
    返回:
        成本效益分析结果
    """
    # 基础统计
    unhedged_annual_return = np.mean(portfolio_returns) * 252 * 100
    hedged_annual_return = np.mean(hedged_returns) * 252 * 100

    unhedged_vol = np.std(portfolio_returns) * np.sqrt(252) * 100
    hedged_vol = np.std(hedged_returns) * np.sqrt(252) * 100

    # 最大回撤
    unhedged_cum = np.cumprod(1 + portfolio_returns)
    hedged_cum = np.cumprod(1 + hedged_returns)
    unhedged_max_dd = np.max(
        1 - unhedged_cum / np.maximum.accumulate(unhedged_cum)
    ) * 100
    hedged_max_dd = np.max(
        1 - hedged_cum / np.maximum.accumulate(hedged_cum)
    ) * 100

    # 下行风险
    unhedged_downside = portfolio_returns[portfolio_returns < 0]
    hedged_downside = hedged_returns[hedged_returns < 0]
    unhedged_downside_vol = np.std(unhedged_downside) * np.sqrt(252) * 100
    hedged_downside_vol = np.std(hedged_downside) * np.sqrt(252) * 100

    # Sortino比率
    sortino_unhedged = unhedged_annual_return / unhedged_downside_vol
    sortino_hedged = hedged_annual_return / hedged_downside_vol

    # 成本拖累
    return_drag = unhedged_annual_return - hedged_annual_return

    return {
        'Unhedged_Ann_Return': unhedged_annual_return,
        'Hedged_Ann_Return': hedged_annual_return,
        'Return_Drag_bps': return_drag,
        'Hedge_Cost_bps': annual_premium_bps,
        'Unhedged_Max_Drawdown': unhedged_max_dd,
        'Hedged_Max_Drawdown': hedged_max_dd,
        'Drawdown_Improvement': unhedged_max_dd - hedged_max_dd,
        'Unhedged_Sortino': sortino_unhedged,
        'Hedged_Sortino': sortino_hedged,
        'Sortino_Improvement': sortino_hedged - sortino_unhedged,
        'Net_Benefit': sortino_hedged > sortino_unhedged
    }
