# @quantlab/output: 871ae5cc
def dynamic_tail_hedge(current_portfolio_value: float,
                        current_drawdown_pct: float,
                        vix_level: float,
                        realized_vol: float,
                        base_hedge_ratio: float = 0.02) -> dict:
    """
    动态尾部对冲决策。

    根据以下信号调整对冲比例：
    1. 组合当前回撤深度
    2. 市场波动率环境
    3. VIX水平（对冲成本）

    参数:
        current_portfolio_value: 当前组合价值
        current_drawdown_pct: 当前回撤百分比（正值）
        vix_level: 当前VIX
        realized_vol: 已实现波动率
        base_hedge_ratio: 基础对冲比例
    返回:
        对冲决策
    """
    # 1. 回撤加速信号：回撤越深，越需要保护（防连续下跌）
    drawdown_factor = 1.0 + current_drawdown_pct / 10  # 每10%回撤加倍

    # 2. 波动率信号：高波动时对冲成本高，适度减少
    vol_percentile = norm.cdf((realized_vol - 0.15) / 0.05)
    vol_factor = 1.0 / max(0.5, vol_percentile + 0.5)

    # 3. VIX信号：VIX低位时多买（便宜），高位时少买（贵）
    vix_factor = 1.0 / max(0.5, min(vix_level / 20, 2.0))

    # 综合调整
    adjusted_hedge_ratio = base_hedge_ratio * \
        drawdown_factor * vol_factor * vix_factor

    # 限制范围：0.5%到10%
    adjusted_hedge_ratio = np.clip(adjusted_hedge_ratio, 0.005, 0.10)

    # 对冲决策
    hedge_amount = current_portfolio_value * adjusted_hedge_ratio

    return {
        'Hedge_Ratio': adjusted_hedge_ratio * 100,
        'Hedge_Amount': hedge_amount,
        'Hedge_Budget': base_hedge_ratio * current_portfolio_value,
        'Is_Over_Hedged': adjusted_hedge_ratio > base_hedge_ratio * 2,
        'Is_Under_Hedged': adjusted_hedge_ratio < base_hedge_ratio * 0.5
    }
