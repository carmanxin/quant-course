# @quantlab/output: fe9c3a4f
from scipy.stats import norm
from scipy.optimize import fsolve

def merton_model(E, D, r, T, sigma_E):
    """
    Merton 结构模型——从权益市值和波动率反推资产价值和资产波动率
    E: 权益市值
    D: 债务面值（默认点）
    r: 无风险利率
    T: 债务期限
    sigma_E: 权益波动率
    """
    def equations(x):
        V, sigma_V = x
        d1 = (np.log(V / D) + (r + 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))

        eq1 = V * norm.cdf(d1) - D * np.exp(-r * T) * norm.cdf(d1 - sigma_V * np.sqrt(T)) - E
        eq2 = V * norm.cdf(d1) * sigma_V / E - sigma_E

        return [eq1, eq2]

    V0, sigma_V0 = E + D, sigma_E * E / (E + D)
    V, sigma_V = fsolve(equations, [V0, sigma_V0])

    # 违约距离 (Distance to Default)
    DD = (np.log(V / D) + (r - 0.5 * sigma_V**2) * T) / (sigma_V * np.sqrt(T))
    PD = norm.cdf(-DD)

    return {
        'asset_value': V,
        'asset_volatility': sigma_V,
        'distance_to_default': DD,
        'default_probability': PD,
        'credit_spread_implied': -np.log(1 - PD * (1 - 0.4)) / T  # 假设40%回收率
    }

# 示例
result = merton_model(E=100, D=80, r=0.03, T=1.0, sigma_E=0.35)
print(f"资产价值: {result['asset_value']:.2f}")
print(f"违约距离: {result['distance_to_default']:.2f}")
print(f"违约概率: {result['default_probability']:.4%}")
