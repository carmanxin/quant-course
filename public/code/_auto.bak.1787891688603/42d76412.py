# @quantlab/output: 42d76412
# 雪球产品 Monte Carlo 分析
def snowball_analysis(S0, coupons, knock_out_levels, knock_in_level,
                      T, dates, r, sigma, n_paths=10000):
    """
    雪球产品收益模拟
    knock_out_levels: list of KO levels at each observation date
    knock_in_level: KI level (typically 0.70-0.80)
    coupons: 票息率（年化）
    """
    n_obs = len(dates)
    dt = np.diff([0] + list(dates))
    paths = np.zeros((n_paths, n_obs + 1))
    paths[:, 0] = S0

    for t in range(1, n_obs + 1):
        Z = np.random.randn(n_paths)
        paths[:, t] = paths[:, t-1] * np.exp(
            (r - 0.5*sigma**2)*dt[t-1] + sigma*np.sqrt(dt[t-1])*Z
        )

    payoffs = np.zeros(n_paths)
    for i in range(n_paths):
        for t in range(1, n_obs + 1):
            if paths[i, t] >= knock_out_levels[t-1]:
                payoffs[i] = S0 * (1 + coupons * dates[t-1])
                break
        else:
            if paths[i, -1] < knock_in_level:
                payoffs[i] = paths[i, -1]
            else:
                payoffs[i] = S0 * (1 + coupons * T)

    # 计算风险指标
    avg_return = (payoffs.mean() / S0 - 1)
    loss_prob = (payoffs < S0).mean()
    var_95 = np.percentile(payoffs, 5)

    return {
        'avg_return': avg_return,
        'loss_prob': loss_prob,
        'var_95': var_95,
        'expected_value': np.exp(-r * T) * payoffs.mean()
    }
