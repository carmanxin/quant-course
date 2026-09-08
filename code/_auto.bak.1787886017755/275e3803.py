# @quantlab/output: 275e3803
def tips_fair_value(real_yield: float,
                     expected_inflation: np.ndarray,
                     inflation_volatility: float = 0.015,
                     maturity_years: int = 10,
                     nominal_par: float = 1000.0) -> float:
    """
    计算TIPS的理论公允价值。

    TIPS价格 = 预期通胀调整后的现金流现值 + 通缩保护期权价值

    参数:
        real_yield: 实际收益率（小数形式，如0.01=1%）
        expected_inflation: 未来各期的预期通胀率数组
        inflation_volatility: 通胀的年度波动率
        maturity_years: 到期年数
        nominal_par: 名义本金
    返回:
        TIPS理论价格
    """
    n_periods = len(expected_inflation)

    # 计算通胀调整后的本金路径
    inflation_index = np.cumprod(1 + expected_inflation)
    inflation_index = np.insert(inflation_index, 0, 1.0)

    # 票息（假设固定票息率）
    coupon_rate = real_yield  # 简化：实际收益率 = 票息率
    coupon = nominal_par * coupon_rate

    # 贴现因子
    discount_factors = (1 + real_yield) ** (-np.arange(1, n_periods + 1))

    # 通胀调整后的现金流
    pv_coupons = np.sum(
        coupon * inflation_index[1:] * discount_factors
    )
    pv_principal = nominal_par * inflation_index[-1] * \
        (1 + real_yield) ** (-n_periods)

    # 通缩保护期权的价值（简化：Black-Scholes类型估值）
    # 在到期日，回报为 max(Par - Adjusted Principal, 0)
    # 简化估计：通胀低于某个阈值的概率
    deflation_prob = np.mean(expected_inflation < 0)  # 负通胀概率
    floor_value = nominal_par * deflation_prob * \
        (1 + real_yield) ** (-n_periods) * 0.5

    fair_value = pv_coupons + pv_principal + floor_value

    return fair_value
