# @quantlab/output: 4c557858
import numpy as np
import pandas as pd
from scipy import stats, optimize
import matplotlib.pyplot as plt

def fit_gpd(exceedances: np.ndarray) -> dict:
    """
    用极大似然估计拟合广义帕累托分布（GPD）。

    参数:
        exceedances: 超过阈值的超出量（正值）
    返回:
        包含 xi, beta, log_likelihood 的字典
    """
    def gpd_neg_loglik(params, data):
        xi, log_beta = params
        beta = np.exp(log_beta)  # 确保正值

        n = len(data)
        if abs(xi) < 1e-8:
            # xi ≈ 0 时的极限情况（指数分布）
            ll = -n * np.log(beta) - np.sum(data) / beta
        else:
            # 标准GPD对数似然
            if np.any(1 + xi * data / beta <= 0):
                return 1e10  # 惩罚不满足支撑域的参数
            ll = -n * np.log(beta) - (1 + 1/xi) * \
                 np.sum(np.log(1 + xi * data / beta))

        return -ll

    # 初始猜测：使用矩估计
    m = np.mean(exceedances)
    v = np.var(exceedances)
    xi0 = 0.5 * (1 - m**2 / v)
    beta0 = 0.5 * m * (1 + m**2 / v)

    result = optimize.minimize(
        gpd_neg_loglik,
        [xi0, np.log(beta0)],
        args=(exceedances,),
        method='Nelder-Mead',
        options={'maxiter': 2000}
    )

    xi_hat = result.x[0]
    beta_hat = np.exp(result.x[1])

    return {
        'xi': xi_hat,
        'beta': beta_hat,
        'log_likelihood': -result.fun,
        'convergence': result.success
    }
