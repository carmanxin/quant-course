import numpy as np
from scipy.optimize import minimize
np.random.seed(42)
n_assets = 5
returns = np.random.randn(500, n_assets) * 0.01 + 0.0005
mean_ret = np.mean(returns, axis=0)
cov_matrix = np.cov(returns.T)
def portfolio_volatility(weights, cov):
    return np.sqrt(weights @ cov @ weights)
def neg_sharpe(weights, mean_ret, cov, rf=0.02/252):
    port_ret = weights @ mean_ret
    port_vol = np.sqrt(weights @ cov @ weights)
    return -(port_ret - rf) / port_vol
constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
bounds = tuple((0, 1) for _ in range(n_assets))
w0 = np.ones(n_assets) / n_assets
result = minimize(neg_sharpe, w0, args=(mean_ret, cov_matrix), method='SLSQP', bounds=bounds, constraints=constraints)
opt_weights = result.x
opt_ret = opt_weights @ mean_ret * 252
opt_vol = np.sqrt(opt_weights @ cov_matrix @ opt_weights) * np.sqrt(252)
print('最优权重:')
for i, w in enumerate(opt_weights):
    print(f'  资产{i+1}: {w*100:.1f}%')
print(f'\n年化收益: {opt_ret*100:.2f}%')
print(f'年化波动: {opt_vol*100:.2f}%')
print(f'夏普比率: {opt_ret/opt_vol:.2f}')
