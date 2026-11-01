# @quantlab/output: e3cf0a43
import numpy as np

S = 2.800
K = 2.700  # 愿意加仓价格(虚值 3.6%)
T = 30/365
r = 0.025
sigma = 0.22  # IV 假设偏高

# 计算卖出 Put 权利金
from scipy.stats import norm
def bs_put(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

put_premium = bs_put(S, K, T, r, sigma)
print(f"标的价: {S}, 卖 K={K} Put 权利金: {put_premium:.4f} 元/份 = {put_premium*10000:.0f} 元/张")
print(f"占组合成本: {put_premium/S*100:.2f}%")

# 4 种到期情景分析
print(f"\n{'到期价':>8} {'Put交割':>10} {'净损益(每张)':>15} {'含义'}")
for ST in [2.50, 2.60, 2.70, 2.80, 2.90, 3.00]:
    payoff = max(K - ST, 0) * 10000
    pnl = put_premium * 10000 - payoff
    if payoff > 0:
        label = f"按 2.700 增持,加上权利金损益"
    else:
        label = f"纯赚权利金 {put_premium*10000:.0f} 元"
    print(f"{ST:>8.2f} {payoff:>10.0f} {pnl:>+15.0f}  {label}")
