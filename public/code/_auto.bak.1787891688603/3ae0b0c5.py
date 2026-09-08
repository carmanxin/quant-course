# @quantlab/output: 3ae0b0c5
# 三种方法定价结果对比
import time

S0, K, T, r, sigma = 100, 100, 1.0, 0.03, 0.25
n_steps = 500

# CRR 二叉树
t0 = time.time()
crr_price = crr_binomial_tree(S0, K, T, r, sigma, n_steps, 'call', american=False)
t_crr = time.time() - t0

# 隐式FDM
t0 = time.time()
fdm_price = implicit_fdm(S0, K, T, r, sigma, S_max=300, n_S=500, n_T=500, option_type='call')
t_fdm = time.time() - t0

# BS 解析解（基准）
from scipy.stats import norm
d1 = (np.log(S0/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
d2 = d1 - sigma*np.sqrt(T)
bs_price = S0*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

print(f"{'方法':<20} {'价格':<12} {'误差':<12} {'耗时':<10}")
print(f"{'BS解析解':<20} {bs_price:<12.6f} {'--':<12} {'--':<10}")
print(f"{'CRR二叉树':<20} {crr_price:<12.6f} {abs(crr_price-bs_price):<12.6f} {t_crr:<10.4f}")
print(f"{'隐式FDM':<20} {fdm_price:<12.6f} {abs(fdm_price-bs_price):<12.6f} {t_fdm:<10.4f}")
