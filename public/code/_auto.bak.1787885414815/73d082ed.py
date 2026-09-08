# @quantlab/output: 73d082ed
# Covered Call 收益分析
S = 2.800
K_short = 2.940  # OTM 5%
T = 30/365
r = 0.025
sigma = 0.18

def bs(S, K, T, r, sigma, otype="call"):
    from scipy.stats import norm
    if T <= 0:
        return max(S-K, 0) if otype=="call" else max(K-S, 0)
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    if otype == "call":
        return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
    return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

call_premium = bs(S, K_short, T, r, sigma, "call")
print(f"卖出 OTM {((K_short-S)/S)*100:.1f}% Call 权利金: {call_premium:.4f} 元/份 = {call_premium*10000:.0f} 元/张")

# 4 种场景分析
print(f"\n{'到期价':>8} {'ETF损益':>10} {'Call损益':>10} {'净损益':>10} {'年化'}")
for ST in [2.50, 2.70, 2.80, 2.90, 2.94, 3.00, 3.10]:
    etf_pnl_per_lot = (ST - S) * 10000  # 持有 1 份 50ETF ×10000
    # 卖出 Call: 收入权利金 - max(ST-K, 0)*10000
    call_pnl_per_lot = call_premium * 10000 - max(ST-K_short, 0)*10000
    net = etf_pnl_per_lot + call_pnl_per_lot
    ann_factor = (365/30)
    print(f"{ST:>8.3f} {etf_pnl_per_lot:>+10.0f} {call_pnl_per_lot:>+10.0f} {net:>+10.0f}  {net*ann_factor/10000*100:>5.2f}%")
