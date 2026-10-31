# @quantlab/output: 12.1-yield-curve
import numpy as np
from scipy.optimize import minimize
def nelson_siegel(t, beta0, beta1, beta2, tau):
    factor = (1 - np.exp(-t/tau)) / (t/tau)
    return beta0 + beta1 * factor + beta2 * (factor - np.exp(-t/tau))
np.random.seed(42)
maturities = np.array([0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30])
true_params = (0.04, -0.02, 0.01, 2.0)
yields = nelson_siegel(maturities, *true_params) + np.random.randn(len(maturities)) * 0.001
def objective(params):
    pred = nelson_siegel(maturities, *params)
    return np.sum((yields - pred)**2)
result = minimize(objective, (0.03, -0.01, 0.02, 1.5), method='Nelder-Mead')
fitted = nelson_siegel(maturities, *result.x)
print(f'拟合参数: beta0={result.x[0]:.4f}, beta1={result.x[1]:.4f}, beta2={result.x[2]:.4f}, tau={result.x[3]:.2f}')
print(f'\n期限\t原始\t拟合')
for t, y, f in zip(maturities, yields, fitted):
    print(f'{t:4.1f}年\t{y*100:.3f}%\t{f*100:.3f}%')
