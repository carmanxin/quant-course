# @quantlab/output: 11.8-vol-trading
"""11.8 波动率交易策略 — 5 大经典策略 Payoff 与 Greeks"""
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# ===== Black-Scholes 定价 =====
def bs(S, K, T, r, sigma, otype="call"):
    if T <= 0:
        return max(S - K, 0) if otype == "call" else max(K - S, 0)
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    if otype == "call":
        return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

def bs_greeks(S, K, T, r, sigma, otype="call"):
    """delta, gamma, theta(日), vega(每 1%), rho(每 1%)"""
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    sign = 1 if otype == "call" else -1
    delta = sign * norm.cdf(sign * d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))
             - sign*r*K*np.exp(-r*T)*norm.cdf(sign*d2)) / 365
    vega = S*norm.pdf(d1)*np.sqrt(T) / 100
    rho = sign*K*T*np.exp(-r*T)*norm.cdf(sign*d2) / 100
    return delta, gamma, theta, vega, rho


# ===== 场景参数 =====
S = 100; r = 0.03; sigma = 0.20
T = 30 / 365
ATM = 100

# 5 大策略 legs (单位: 1张 = 100份,但这里用每股)
def long_call(K=100):   return ("+1 Call K=100", +1, "call", K)
def long_put(K=100):    return ("+1 Put  K=100", +1, "put",  K)
def short_call(K=100):  return ("-1 Call K=100", -1, "call", K)
def short_put(K=100):   return ("-1 Put  K=100", -1, "put",  K)

strategies = {
    "Long Call (单边看涨)": [long_call],
    "Long Put  (单边看跌)": [long_put],
    "Long Straddle (跨式做多)": [long_call, long_put],
    "Long Strangle (宽跨式)": [
        long_call(K=105), short_call(K=105)._replace if False else (None,),
    ],
}
# 重做 — 不用上面 hack
strategies = {
    "Long Straddle\n(ATM Call+Put)":
        [(+1, "call", 100), (+1, "put",  100)],
    "Long Strangle\n(OTM Call+Put)":
        [(+1, "call", 105), (+1, "put",   95)],
    "Short Strangle\n(收入时间价值)":
        [(-1, "call", 105), (-1, "put",   95)],
    "Long Butterfly\n(限定最大亏损)":
        [(+1, "call", 95), (-2, "call", 100), (+1, "call", 105)],
    "Iron Condor\n(卖方四腿)":
        [(-1, "put", 95), (+1, "put",  90),
         (-1, "call", 105), (+1, "call", 110)],
    "Bull Call Spread\n(牛市价差)":
        [(+1, "call", 100), (-1, "call", 105)],
}

# ===== Payoff 计算 =====
def payoff_at_expiry(legs, S_T, r, T):
    pnl = 0
    for qty, otype, K in legs:
        if otype == "call":
            intrinsic = max(S_T - K, 0)
        else:
            intrinsic = max(K - S_T, 0)
        # 买入期权成本
        cost = bs(S, K, T, r, sigma, otype)
        pnl += qty * (intrinsic - cost)
    return pnl * 100  # 乘 100 假设每张 100 份


S_range = np.linspace(70, 130, 200)

# ===== Plot 6 个策略的 Payoff =====
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for i, (name, legs) in enumerate(strategies.items()):
    payoffs = [payoff_at_expiry(legs, s, r, T) for s in S_range]
    ax = axes[i]
    ax.plot(S_range, payoffs, color="#00E5A0", linewidth=2)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_title(name, fontsize=11)
    ax.set_xlabel("到期标的价格")
    ax.set_ylabel("损益 (元 / 股×100)")
    ax.grid(alpha=0.3)
    # 标注最大盈亏
    p_arr = np.array(payoffs)
    if p_arr.max() > 0:
        ax.text(S_range[p_arr.argmax()], p_arr.max(), f"最大收益 {p_arr.max():.0f}",
                ha="center", color="#FF0080", fontsize=9)
    if p_arr.min() < 0:
        ax.text(S_range[p_arr.argmin()], p_arr.min(), f"最大亏损 {p_arr.min():.0f}",
                ha="center", color="#FF4D6D", fontsize=9)

plt.suptitle("5+1 个波动率策略到期 Payoff 图 (S=100, T=30d, σ=20%, r=3%)",
             fontsize=14, fontweight="bold")
plt.tight_layout()

# ===== 静态输出每个策略的盈亏和 Greeks =====
print("=" * 70)
print(f"{'策略':<24} {'最大收益':>10} {'最大亏损':>10} {'盈亏平衡点'}")
print("=" * 70)
for name, legs in strategies.items():
    payoffs = np.array([payoff_at_expiry(legs, s, r, T) for s in S_range])
    max_p = payoffs.max()
    min_p = payoffs.min()
    breakeven = "—"
    for j in range(len(S_range)-1):
        if payoffs[j] * payoffs[j+1] < 0:
            breakeven = f"{S_range[j]:.2f}"
            break
    name_clean = name.replace("\n", " ")
    print(f"{name_clean:<24} {max_p:>10.1f} {min_p:>10.1f} {breakeven:>10}")

print("\n策略解读:")
print("  Long Straddle: 做多波动率, 期权费是最大亏损, 标的大幅波动可大幅获利")
print("  Short Strangle: 卖时间价值, 最大收益=总收入期权费, 尾端风险极大")
print("  Long Butterfly: 低波动+温和预期, 最大亏损有限, 适合 IV 较高时卖出")
print("  Iron Condor: 在 short strangle 基础上再买两腿保护, 风险/收益可控")
print("  Bull Call Spread: 锁定最大亏损, 温和看涨, 适合预期小涨")

# Greeks 分析(以 Long Straddle 为例)
print("\n=== Long Straddle 的 Greeks 叠加 ===")
legs = strategies["Long Straddle\n(ATM Call+Put)"]
total = {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}
for qty, otype, K in legs:
    d, g, t, v, _ = bs_greeks(S, K, T, r, sigma, otype)
    total["delta"] += qty*d; total["gamma"] += qty*g
    total["theta"] += qty*t; total["vega"] += qty*v
    print(f"  {otype:>4} K={K}: Δ={d:+.4f} Γ={g:.4f} Θ={t:.4f} ν={v:.4f}")
print(f"  合计           : Δ={total['delta']:+.4f} Γ={total['gamma']:+.4f} "
      f"Θ={total['theta']:+.4f} ν={total['vega']:+.4f}")
