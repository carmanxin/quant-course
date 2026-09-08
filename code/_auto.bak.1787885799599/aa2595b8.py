# @quantlab/output: aa2595b8
import numpy as np
from scipy.optimize import minimize

def mvo_min_variance(mu, Sigma, target_return=None):
    """
    均值-方差优化

    Parameters:
        mu: 期望收益向量 (N,)
        Sigma: 协方差矩阵 (N, N)
        target_return: 目标收益；None时输出最小方差组合
    Returns:
        weights: 最优权重向量
    """
    n = len(mu)

    def portfolio_variance(w):
        return w @ Sigma @ w

    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]  # 权重和为1

    if target_return is not None:
        constraints.append({'type': 'eq', 'fun': lambda w: w @ mu - target_return})

    bounds = [(0, 1) for _ in range(n)]  # 不允许卖空
    w0 = np.ones(n) / n

    result = minimize(portfolio_variance, w0, method='SLSQP',
                      bounds=bounds, constraints=constraints)
    return result.x

def build_efficient_frontier(mu, Sigma, n_points=50, rf=0.02):
    """构建有效前沿"""
    gmv = mvo_min_variance(mu, Sigma)  # 最小方差组合
    min_ret = gmv @ mu
    max_ret = mu.max()

    target_returns = np.linspace(min_ret, max_ret, n_points)
    frontier = []

    for target in target_returns:
        try:
            w = mvo_min_variance(mu, Sigma, target_return=target)
            port_ret = w @ mu
            port_vol = np.sqrt(w @ Sigma @ w)
            sharpe = (port_ret - rf) / port_vol
            frontier.append({
                'return': port_ret,
                'volatility': port_vol,
                'sharpe': sharpe,
                'weights': w
            })
        except Exception:
            continue

    return pd.DataFrame(frontier)
