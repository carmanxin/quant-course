# @quantlab/output: 8e65dca0
from scipy.optimize import minimize

def nelson_siegel(tau, beta0, beta1, beta2, lam):
    """Nelson-Siegel 模型 —— 即期利率关于期限的函数"""
    x = tau / lam
    factor_loading = (1 - np.exp(-x)) / x
    return (
        beta0
        + beta1 * factor_loading
        + beta2 * (factor_loading - np.exp(-x))
    )

def fit_nelson_siegel(maturities, yields):
    """拟合 Nelson-Siegel 参数"""
    def objective(params):
        beta0, beta1, beta2, lam = params
        predicted = nelson_siegel(maturities, beta0, beta1, beta2, lam)
        return np.sum((predicted - yields)**2)

    result = minimize(objective, [0.03, -0.02, 0.01, 2.0],
                     bounds=[(-0.1, 0.2), (-0.3, 0.3), (-0.3, 0.3), (0.1, 30.0)])
    return result.x
