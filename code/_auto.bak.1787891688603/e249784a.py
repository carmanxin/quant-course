# @quantlab/output: e249784a
def optimal_lp_range(volatility_daily, expected_fee_apr, horizon_days, risk_tolerance=0.05):
    """
    基于波动率确定最优做市区间
    volatility_daily: 资产日波动率
    expected_fee_apr: 预期年化手续费收益
    horizon_days: 做市期限（天）
    risk_tolerance: 愿意接受的IL上限
    """
    # 预期价格变动范围（基于波动率）
    vol_period = volatility_daily * np.sqrt(horizon_days)

    # 使用 Black-Scholes 风格的置信区间
    from scipy.stats import norm
    z_score = norm.ppf(1 - risk_tolerance / 2)  # 双边置信度

    # 价格倍数的上下限
    P_upper_mult = np.exp(z_score * vol_period)
    P_lower_mult = np.exp(-z_score * vol_period)

    # 检查此范围下的最大IL是否可接受
    max_il = max(impermanent_loss(P_upper_mult), impermanent_loss(P_lower_mult))
    expected_net = expected_fee_apr * horizon_days / 365 - max_il

    return {
        'upper_mult': P_upper_mult,
        'lower_mult': P_lower_mult,
        'max_impermanent_loss': max_il,
        'expected_fee_income': expected_fee_apr * horizon_days / 365,
        'expected_net_return': expected_net,
        'recommended': expected_net > 0
    }
