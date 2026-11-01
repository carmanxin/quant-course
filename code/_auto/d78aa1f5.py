# @quantlab/output: d78aa1f5
import numpy as np
from scipy.optimize import minimize

def risk_parity_weights(Sigma):
    """
    风险平价：使每个资产的风险贡献相等

    Parameters:
        Sigma: 协方差矩阵 (N, N)
    Returns:
        weights: 风险平价权重
    """
    n = Sigma.shape[0]

    def risk_contributions(w):
        """计算各资产的风险贡献"""
        port_vol = np.sqrt(w @ Sigma @ w)
        marginal_contrib = Sigma @ w  # 边际风险贡献
        risk_contrib = w * marginal_contrib / port_vol  # 风险贡献
        return risk_contrib

    def objective(w):
        """目标函数：最小化风险贡献的方差"""
        rc = risk_contributions(w)
        target_rc = 1.0 / n  # 目标：每个资产贡献相等
        return np.sum((rc - target_rc) ** 2)

    # 约束
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]  # 权重和为1
    bounds = [(0, 1) for _ in range(n)]  # 不允许卖空

    w0 = np.ones(n) / n
    result = minimize(objective, w0, method='SLSQP',
                      bounds=bounds, constraints=constraints)

    return result.x

def risk_budgeting(Sigma, risk_budgets=None):
    """
    风险预算（Risk Budgeting）：广义的风险平价

    允许不同资产有不同的目标风险贡献

    Parameters:
        Sigma: 协方差矩阵
        risk_budgets: 各资产的目标风险预算（自动归一化），None时等风险贡献
    """
    n = Sigma.shape[0]
    if risk_budgets is None:
        risk_budgets = np.ones(n) / n
    else:
        risk_budgets = np.array(risk_budgets)
        risk_budgets = risk_budgets / risk_budgets.sum()

    def objective(w):
        port_vol = np.sqrt(w @ Sigma @ w)
        rc = w * (Sigma @ w) / port_vol
        return np.sum((rc - risk_budgets) ** 2)

    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = [(0, 1) for _ in range(n)]

    w0 = np.ones(n) / n
    result = minimize(objective, w0, method='SLSQP',
                      bounds=bounds, constraints=constraints)

    return result.x
