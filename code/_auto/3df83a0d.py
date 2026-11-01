# @quantlab/output: 3df83a0d
def mc_control_variate(S0, K, T, r, sigma, n_paths):
    """
    使用几何亚式期权作为控制变量为算术亚式期权定价
    """
    n_steps = 12
    dt = T / n_steps

    Z = np.random.randn(n_paths, n_steps)
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0

    for t in range(1, n_steps + 1):
        S[:, t] = S[:, t-1] * np.exp((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z[:, t-1])

    # 算术平均亚式期权 payoff
    arith_avg = S[:, 1:].mean(axis=1)
    payoff_arith = np.maximum(arith_avg - K, 0)

    # 几何平均亚式期权 payoff（有解析解）
    geom_avg = np.exp(np.log(S[:, 1:]).mean(axis=1))
    payoff_geom = np.maximum(geom_avg - K, 0)

    # 几何平均亚式期权的解析价格
    sigma_adj = sigma * np.sqrt((n_steps+1)*(2*n_steps+1)/(6*n_steps**2))
    mu_adj = 0.5 * (r - 0.5*sigma**2) + 0.5 * sigma_adj**2
    # ... (完整解析解此处省略)

    # 控制变量
    cov = np.cov(payoff_arith, payoff_geom)[0, 1]
    var_geom = np.var(payoff_geom)
    beta = cov / var_geom

    price_raw = np.exp(-r*T) * payoff_arith.mean()
    price_geom = np.exp(-r*T) * payoff_geom.mean()
    geom_true = price_geom  # 此处应用解析解替代

    price_cv = price_raw - beta * (price_geom - geom_true)
    return price_cv, price_raw
