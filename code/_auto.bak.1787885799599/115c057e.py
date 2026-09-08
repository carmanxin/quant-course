# @quantlab/output: 115c057e
def risk_budget_optimization(cov_matrix: np.ndarray,
                              risk_budgets: np.ndarray,
                              max_iter: int = 1000,
                              tol: float = 1e-8) -> np.ndarray:
    """
    风险预算优化：找到使风险贡献等于指定预算的权重。

    风险贡献 RC_i = w_i * (Σw)_i / σ_P

    参数:
        cov_matrix: (N, N) 协方差矩阵
        risk_budgets: (N,) 目标风险预算比例（总和为1）
        max_iter: 最大迭代次数
        tol: 收敛容忍度
    返回:
        最优权重向量
    """
    N = len(risk_budgets)
    weights = np.ones(N) / N  # 初始等权

    for iteration in range(max_iter):
        # 当前组合
        portfolio_std = np.sqrt(weights @ cov_matrix @ weights)
        marginal_risk = cov_matrix @ weights / portfolio_std
        risk_contribution = weights * marginal_risk
        current_budgets = risk_contribution / np.sum(risk_contribution)

        # 检查收敛
        max_deviation = np.max(np.abs(current_budgets - risk_budgets))
        if max_deviation < tol:
            break

        # 调整权重：风险预算不足的资产增加权重
        adjustment = risk_budgets / (current_budgets + 1e-10)
        weights = weights * adjustment

        # 归一化
        weights = weights / np.sum(weights)

    return weights
