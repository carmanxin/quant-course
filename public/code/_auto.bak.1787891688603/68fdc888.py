# @quantlab/output: 68fdc888
def constrained_mvo(mu, Sigma, constraints_config):
    """
    带复杂约束的MVO

    constraints_config example:
    {
        'max_weight': 0.1,          # 单只股票上限10%
        'min_weight': 0.0,          # 不允许卖空
        'industry_exposure': {       # 行业暴露上限
            'tech': 0.3,
            'finance': 0.2,
        },
        'turnover_limit': 0.3,      # 换手率上限（需要当前持仓）
        'current_weights': None,    # 当前持仓权重
    }
    """
    n = len(mu)

    def objective(w):
        return w @ Sigma @ w

    # 约束条件
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]

    # 如有目标收益
    if 'target_return' in constraints_config:
        constraints.append(
            {'type': 'eq', 'fun': lambda w: w @ mu - constraints_config['target_return']}
        )

    # 权重边界
    bounds = [(constraints_config.get('min_weight', 0),
               constraints_config.get('max_weight', 1)) for _ in range(n)]

    # 行业暴露约束（需要行业映射表）
    if 'industry_mapping' in constraints_config and 'industry_exposure' in constraints_config:
        industry_mapping = constraints_config['industry_mapping']
        for ind, max_exp in constraints_config['industry_exposure'].items():
            ind_mask = np.array([industry_mapping.get(i) == ind for i in range(n)], dtype=float)
            constraints.append(
                {'type': 'ineq', 'fun': lambda w, m=ind_mask, e=max_exp: e - w @ m}
            )

    # 换手率约束
    if 'current_weights' in constraints_config and 'turnover_limit' in constraints_config:
        current_w = np.array(constraints_config['current_weights'])
        max_turnover = constraints_config['turnover_limit']

        def turnover_constraint(w):
            return max_turnover - np.sum(np.abs(w - current_w)) / 2
        constraints.append({'type': 'ineq', 'fun': turnover_constraint})

    w0 = np.ones(n) / n
    result = minimize(objective, w0, method='SLSQP',
                      bounds=bounds, constraints=constraints)

    if result.success:
        return result.x
    else:
        raise ValueError(f"优化失败: {result.message}")
