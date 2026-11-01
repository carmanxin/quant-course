# @quantlab/output: cc1856cc
def ac_numerical_optimization(X: float,
                               T: float,
                               N: int,
                               sigma: float,
                               gamma: float,
                               eta: float,
                               risk_aversion: float,
                               g_func: Callable = None,
                               h_func: Callable = None) -> np.ndarray:
    """
    当冲击函数非线性时，用数值优化求解最优执行轨迹。

    参数:
        g_func: 永久冲击函数 g(v)，默认为线性 g(v)=gamma*v
        h_func: 临时冲击函数 h(v)，默认为线性 h(v)=eta*v
    返回:
        最优剩余头寸轨迹
    """
    if g_func is None:
        g_func = lambda v: gamma * v
    if h_func is None:
        h_func = lambda v: eta * v

    tau = T / N

    def objective(n):
        """目标函数：期望成本 + λ * 风险"""
        x = X - np.cumsum(n)
        x_full = np.concatenate([[X], x])

        # 永久冲击成本
        perm_cost = np.sum(tau * x_full[1:] * g_func(n / tau))

        # 临时冲击成本
        temp_cost = np.sum(n * h_func(n / tau))

        expected_cost = perm_cost + temp_cost

        # 风险项
        risk = sigma ** 2 * tau * np.sum(x_full[1:] ** 2)

        return expected_cost + risk_aversion * risk

    def constraint(n):
        """约束：总执行量 = X"""
        return np.sum(n) - X

    # 初始猜测：均匀执行
    n0 = np.ones(N) * X / N

    cons = {'type': 'eq', 'fun': constraint}
    bounds = [(0, X) for _ in range(N)]

    result = minimize(objective, n0, method='SLSQP',
                      bounds=bounds, constraints=cons,
                      options={'maxiter': 1000, 'ftol': 1e-12})

    if not result.success:
        print(f"优化警告: {result.message}")

    n_opt = result.x
    x_opt = np.concatenate([[X], X - np.cumsum(n_opt)])

    return x_opt
