# @quantlab/output: 876f7a28
def cds_pricing(hazard_rates, discount_factors, recovery_rate, times):
    """
    CDS 定价 —— 从违约强度曲线计算公平 CDS 利差
    hazard_rates: 各期的风险率（违约强度）
    discount_factors: 各期的无风险折现因子
    recovery_rate: 回收率
    times: 保费支付时间点
    """
    n = len(times)
    dt = np.diff([0] + list(times))
    survival_prob = np.ones(n)

    # 计算生存概率
    for i in range(1, n):
        survival_prob[i] = survival_prob[i-1] * np.exp(-hazard_rates[i-1] * dt[i-1])

    # 保费端的现值
    premium_leg = 0
    for i, t in enumerate(times):
        premium_leg += discount_factors[i] * survival_prob[i] * dt[i]

    # 保护端：在每个时间区间内发生违约的预期赔偿
    protection_leg = 0
    for i in range(1, n):
        prob_default_in_interval = survival_prob[i-1] - survival_prob[i]
        protection_leg += discount_factors[i] * prob_default_in_interval * (1 - recovery_rate)

    cds_spread = protection_leg / premium_leg
    return cds_spread
