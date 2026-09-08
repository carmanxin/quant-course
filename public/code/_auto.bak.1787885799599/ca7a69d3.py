# @quantlab/output: ca7a69d3
# 详细分解 Long Straddle 各 Greek 对 PnL 的贡献
S, K, T, r, sigma = 100, 100, 30/365, 0.03, 0.20

# Straddle 起始 GREEKS
ds = bs(S, K, T, r, sigma, "call"); ps = bs(S, K, T, r, sigma, "put")
cd, cg, cv, ct = greeks(S, K, T, r, sigma, "call")
pd_, pg, pv, pt = greeks(S, K, T, r, sigma, "put")
print(f"Long Straddle 期初 GREEKS (×10000 份):")
print(f"  Call: Δ={cd:+.4f} Γ={cg:.4f} ν={cv:+.4f} Θ={ct:+.4f}")
print(f"  Put:  Δ={pd_:+.4f} Γ={pg:.4f} ν={pv:+.4f} Θ={pt:+.4f}")
print(f"  合计: Δ={cd+pd_:+.4f} Γ={cg+pg:.4f} ν={cv+pv:+.4f} Θ={ct+pt:+.4f}")
print(f"  期初权利金支出: {(ds+ps)*10000:.0f} 元/对(2张)")

# 模拟 1 周后情景: 标的小涨 +1%, IV 上升 + 2%, 时间 - 7 天
S_new = 101
T_new = 23/365
sigma_new = 0.22

ds_new = bs(S_new, K, T_new, r, sigma_new, "call")
ps_new = bs(S_new, K, T_new, r, sigma_new, "put")
P_total = (ds_new + ps_new - ds - ps) * 10000
print(f"\n1 周后: S={S_new} IV={sigma_new*100:.0f}% T={T_new*365:.0f}天")
print(f"  组合价值变化: {P_total:.0f} 元")
print(f"  风险预警: 因为 Gamma > 0, 标的大幅下跌仍可盈利,但 Theta 累积亏损已达{(ct+pt)*7:.0f}元")
