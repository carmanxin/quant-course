# @quantlab/output: 70d6b3a9
def multi_asset_kelly(mu, Sigma, kelly_fraction=0.5, max_weight=0.3):
    """
    多资产凯利配置：最大化对数效用

    等价于MVO的切线组合，但明确重视长期增长率

    Parameters:
        mu: 期望收益向量
        Sigma: 协方差矩阵
        kelly_fraction: 分数凯利（在总配置基础上打折）
        max_weight: 单一资产最大权重
    """
    from scipy.optimize import minimize

    n = len(mu)

    # 对数效用的确定性等价
    def neg_log_utility(w):
        port_mu = w @ mu
        port_var = w @ Sigma @ w
        # E[log(W)] ≈ log(W0) + μ - σ²/2
        return -(port_mu - 0.5 * port_var)

    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0, max_weight) for _ in range(n)]

    w0 = np.ones(n) / n
    result = minimize(neg_log_utility, w0, method='SLSQP',
                      bounds=bounds, constraints=constraints)

    optimal_unconstrained = result.x

    # 分数凯利：缩减到无风险资产
    # 如果kelly_fraction < 1，将部分资金配置到现金
    risky_weights = optimal_unconstrained * kelly_fraction
    cash_weight = 1 - kelly_fraction

    final_weights = np.append(risky_weights, cash_weight)

    return final_weights  # 最后一个是现金权重
