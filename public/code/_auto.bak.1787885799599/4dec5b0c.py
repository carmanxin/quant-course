# @quantlab/output: 4dec5b0c
def build_swap_curve(market_swap_rates, maturities, interpolation='linear'):
    """
    从市场互换利率构建互换曲线
    market_swap_rates: 不同期限的互换利率报价
    maturities: 对应的期限（年）
    返回：折现因子曲线
    """
    n = len(maturities)
    discount_factors = np.zeros(n)

    for i in range(n):
        T = maturities[i]
        swap_rate = market_swap_rates[i]
        dt = 0.5  # 假设半年付息一次
        n_periods = int(T / dt)

        # 对已知的折现因子进行插值
        if i == 0:
            # 第一个点：假设只有一个支付期
            discount_factors[i] = 1.0 / (1.0 + swap_rate * T)
        else:
            # bootstrap: 从市场互换利率反推
            pv_fixed_known = 0
            for j in range(1, n_periods):
                t_j = j * dt
                # 插值得到该期限的折现因子
                if t_j < maturities[i-1]:
                    df_j = np.interp(t_j, maturities[:i], discount_factors[:i])
                else:
                    df_j = discount_factors[i-1]
                pv_fixed_known += swap_rate * dt * df_j

            # 最后一期现金流的折现因子
            discount_factors[i] = (1.0 - swap_rate * dt * pv_fixed_known) \
                                  / (1.0 + swap_rate * dt)

    return maturities, discount_factors
