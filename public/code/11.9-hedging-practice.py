"""11.9 套保策略实战 — Delta / Gamma / Vega 套保三个案例"""
import numpy as np
from scipy.stats import norm

# ===== Black-Scholes + Greeks =====
def bs(S, K, T, r, sigma, otype="call"):
    if T <= 0:
        return max(S-K,0) if otype=="call" else max(K-S,0)
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    if otype == "call":
        return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

def greeks(S, K, T, r, sigma, otype="call"):
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    sign = 1 if otype=="call" else -1
    delta = sign * norm.cdf(sign * d1)
    gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
    theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))
             - sign*r*K*np.exp(-r*T)*norm.cdf(sign*d2)) / 365
    vega = S*norm.pdf(d1)*np.sqrt(T) / 100
    return delta, gamma, theta, vega


# ============================================================
# 案例 1: Delta 套保 (静态)
# ============================================================
print("=" * 70)
print("案例 1: 沪深 300 看跌期权 Delta 套保 50ETF 持仓")
print("=" * 70)
print("场景: 持有 100 万份 50ETF, 现价 2.800, 担心下跌, 买入看跌")
print()

portfolio_value = 2.800 * 1000000  # 280 万元
S = 2.800; K = 2.800; T = 60/365; r = 0.025; sigma = 0.22
put_delta, put_gamma, _, put_vega = greeks(S, K, T, r, sigma, "put")
print(f"  50ETF 持仓 Delta:  {+1000000:>12,.0f}")
print(f"  Put期权 Delta:     {put_delta:>12.4f}  (每张对应10000份)")
print(f"  Put期权 Gamma:     {put_gamma:>12.4f}")
print(f"  Put期权 Vega:      {put_vega:>12.4f}")

contracts_to_buy = int(-1000000 / (put_delta * 10000))
print(f"\n  套保所需 Put 合约数: {contracts_to_buy} 张")
print(f"  套保成本:             {bs(S,K,T,r,sigma,'put')*10000*contracts_to_buy:>10,.0f} 元")
print(f"  占组合比例:           {bs(S,K,T,r,sigma,'put')*10000*contracts_to_buy/portfolio_value*100:.2f}%")

# 验证对冲后 Delta 中性
total_delta = 1000000 + contracts_to_buy*put_delta*10000
print(f"  对冲后组合 Delta:    {total_delta:>12.2f} (≈0 即中性)")

# 模拟不同标的价格下的组合价值
print("\n标的价格变动 → 持仓损益:")
print(f"{'标的价格':>8} {'ETF损益':>10} {'Put损益':>10} {'净额':>10}")
for new_S in np.linspace(2.50, 3.00, 6):
    etf_pnl = (new_S - S) * 1000000
    put_pnl = (bs(new_S, K, max((T-1/365)*T, 0.001), r, sigma, "put") - bs(S,K,T,r,sigma,"put")) * 10000 * contracts_to_buy
    print(f"{new_S:8.3f} {etf_pnl:10,.0f} {put_pnl:10,.0f} {etf_pnl+put_pnl:10,.0f}")


# ============================================================
# 案例 2: 卖出看跌的备兑策略 (Covered Put)
# ============================================================
print("\n" + "=" * 70)
print("案例 2: 长期持有 + 卖出虚值看跌 (Covered Put) 增厚收益")
print("=" * 70)
print("场景: 长期看好 50ETF, 愿意在更低价位增持, 卖出虚值 Put 收权利金")
print()

S = 2.800; K = 2.700  # OTM 5% out
T = 30/365; r = 0.025; sigma = 0.22
put_premium = bs(S, K, T, r, sigma, "put")
print(f"  标的现价: {S}, 卖出 Put 行权价: {K} (虚值 {(1-K/S)*100:.1f}%)")
print(f"  权利金收入: {put_premium:.4f}/份 = {put_premium*10000:.0f} 元/张")
print(f"\n到期情景分析 (每张合约):")
print(f"{'到期价':>8} {'Put交割':>10} {'净损益':>10}")
for ST in [2.50, 2.60, 2.70, 2.80, 2.90, 3.00]:
    payoff = max(K - ST, 0)
    pnl = put_premium - payoff
    label = "被行权,按行权价买入" if payoff > 0 else "未行权,纯赚权利金"
    print(f"{ST:8.3f} {payoff:10.4f} {pnl:10.4f}  {label}")


# ============================================================
# 案例 3: Gamma-Vega 联合套保 (动态)
# ============================================================
print("\n" + "=" * 70)
print("案例 3: Long 1 张 50ETF ATM Put 后, 用跨期对冲 Gamma/Vega")
print("=" * 70)
print("场景: 持有 ATM Put 到期日 T1=30天. 用 T2=90 天的 OTM Put 对冲 Gamma/Vega")
print()

# 持仓: Short T1=30d ATM Put  (假设做市商)
# 用 Long T2=90d OTM Put 对冲
opt_held = {"S": 2.800, "K": 2.800, "T": 30/365, "otype": "put", "qty": -1}
opt_hedge = {"S": 2.800, "K": 2.700, "T": 90/365, "otype": "put", "qty": +1}

delta_h, gamma_h, theta_h, vega_h = greeks(opt_held["S"], opt_held["K"],
                                            opt_held["T"], r, sigma, opt_held["otype"])
delta_2, gamma_2, theta_2, vega_2 = greeks(opt_hedge["S"], opt_hedge["K"],
                                            opt_hedge["T"], r, sigma, opt_hedge["otype"])
print(f"  持仓 Put T1 ATM:")
print(f"    Δ={delta_h:.4f} Γ={gamma_h:.4f} ν={vega_h:.4f}")
print(f"  对冲 Put T2 OTM:")
print(f"    Δ={delta_2:.4f} Γ={gamma_2:.4f} ν={vega_2:.4f}")

# Gamma 中性所需对冲张数
contracts_hedge = -gamma_h / gamma_2
print(f"\n  Gamma 中性对冲比例: {contracts_hedge:.2f} 张 (T2 OTM Put)")

# 调整合约数后, Gamma 中性但 Delta/Vega 还残留
gamma_total = -1 * gamma_h + contracts_hedge * gamma_2
vega_total  = -1 * vega_h  + contracts_hedge * vega_2
delta_total = -1 * delta_h + contracts_hedge * delta_2
print(f"  调整后:")
print(f"    总 Gamma: {gamma_total:.6f} (≈0)")
print(f"    总 Vega:  {vega_total:+.4f}  (残留, 可再用第三个腿对冲)")
print(f"    总 Delta: {delta_total:+.4f}  (残留, 需用标的调整)")
