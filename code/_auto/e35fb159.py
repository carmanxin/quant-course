# @quantlab/output: e35fb159
import numpy as np
from scipy.stats import norm

def bs_greeks(S, K, T, r, sigma, option_type='call'):
    """
    计算 Black-Scholes 模型下的所有 Greeks
    S: 标的资产价格
    K: 行权价
    T: 到期时间（年）
    r: 无风险利率
    sigma: 波动率
    option_type: 'call' 或 'put'
    """
    d1 = (np.log(S/K) + (r + sigma**2/2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    sign = 1 if option_type == 'call' else -1

    delta = sign * norm.cdf(sign * d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (
        -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
        - sign * r * K * np.exp(-r * T) * norm.cdf(sign * d2)
    )
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho = sign * K * T * np.exp(-r * T) * norm.cdf(sign * d2) / 100

    return {'delta': delta, 'gamma': gamma, 'theta': theta,
            'vega': vega, 'rho': rho}

# 示例：ATM 看涨期权的 Greeks
greeks = bs_greeks(S=100, K=100, T=30/365, r=0.03, sigma=0.20, option_type='call')
for g, v in greeks.items():
    print(f"{g:>8}: {v:.4f}")
