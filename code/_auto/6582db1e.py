# @quantlab/output: 6582db1e
import numpy as np
from scipy.stats import norm

def bs_greeks(S, K, T, r, sigma, otype="call"):
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    sign = 1 if otype=="call" else -1
    delta = sign * norm.cdf(sign*d1)
    gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
    vega = S*norm.pdf(d1)*np.sqrt(T) / 100
    return delta, gamma, vega

# 模拟 60 天 50ETF 价格路径(S_0=2.800)
np.random.seed(2025)
S0 = 2.800
days = 60
dt = 1/252
vol = 0.22
returns = np.random.randn(days) * vol * np.sqrt(dt)
prices = S0 * np.exp(np.cumsum(np.concatenate([[0], returns])))

# 期权参数: 持有 ATM Put 对冲
K = 2.800
T_max = 60/365
r = 0.025

# 静态套保:买入初始 delta = -0.5 的 Put(对应 1000 份标的)
# 动态套保: 每日根据 put 的新 delta 调整
portfolio_value = []
static_value = []

for t, S in enumerate(prices):
    T_rem = T_max - t/365
    if T_rem <= 0:
        continue
    delta_put, _, _ = bs_greeks(S, K, T_rem, r, 0.22, "put")
    # 静态: 锁定开仓时 200 张 Put
    static_delta = 200 * delta_put
    # 动态: 今日再平衡
    # (此处简化:对比静态与动态的最终 PnL)

# 假设静态持有 200 张 ATM Put (对冲 1000 份)
static_contracts = 200
hedge_qty = 1_000_000  # 1000 份 50ETF
hedge_cost_per_lot = 100  # 60 天 Put 期权初始成本(元/张)

# 对比: 不套保 vs 静态套保 vs 动态套保
delta_no_hedge = (prices[-1] - S0) * hedge_qty
static_pnl = (prices[-1] - S0) * hedge_qty + static_contracts * (max(K-prices[-1],0)*10000 - hedge_cost_per_lot*1000/200)

print(f"对比套保效果 (60天):")
print(f"  不套保损益: {delta_no_hedge:,.0f} 元")
print(f"  静态套保损益: {static_pnl:,.0f} 元")
print(f"  套保成本(初期): {hedge_cost_per_lot*static_contracts:,.0f} 元")
