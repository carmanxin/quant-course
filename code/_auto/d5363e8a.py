# @quantlab/output: d5363e8a
def bootstrap_cds_curve(cds_spreads, maturities, recovery_rate, discount_curve):
    """
    从 CDS 报价构建信用曲线（分段常数风险率）
    cds_spreads: 各期限 CDS 利差
    maturities: 期限
    recovery_rate: 回收率
    discount_curve: 函数，输入期限返回折现因子
    """
    n = len(maturities)
    hazard_rates = np.zeros(n)

    for i in range(n):
        T = maturities[i]
        S = cds_spreads[i]
        dt = 0.25  # 季度支付
        times = np.arange(dt, T + dt, dt)

        # 使用二分法求解该段的风险率
        lo, hi = 0.0, 0.5
        for _ in range(50):
            mid = (lo + hi) / 2
            test_hazards = np.array(list(hazard_rates[:i]) + [mid] * (len(times) - i + 1))
            test_spread = cds_pricing(test_hazards,
                                      np.array([discount_curve(t) for t in times]),
                                      recovery_rate, times)
            if test_spread < S:
                lo = mid
            else:
                hi = mid

        hazard_rates[i] = (lo + hi) / 2

    return maturities, hazard_rates
