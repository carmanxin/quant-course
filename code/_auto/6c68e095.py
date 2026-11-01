# @quantlab/output: 6c68e095
# 完整 BS 二阶 Greeks 计算框架
def bs_greeks_full(S, K, T, r, sigma):
    """完整 Black-Scholes 一阶 + 二阶 Greeks"""
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)

    sign = 1  # 默认为 Call
    # 一阶
    delta = sign * cdf_d1
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    theta = (-S*pdf_d1*sigma/(2*np.sqrt(T))
             - sign*r*K*np.exp(-r*T)*cdf_d2)/365
    vega = S*pdf_d1*np.sqrt(T) / 100

    # 二阶
    vanna = -pdf_d1 * d2 / sigma  # ∂Δ/∂σ
    vomma = vega * d1 * d2 / sigma  # ∂V/∂σ^2
    charm = -pdf_d1 * (2*r*T - d2*sigma*np.sqrt(T)) / (2*T*sigma*np.sqrt(T))  # ∂Δ/∂t
    speed = -gamma / S * (d1 / (sigma*np.sqrt(T)) + 1)  # ∂Γ/∂S

    return {
        'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega,
        'vanna': vanna, 'vomma': vomma, 'charm': charm, 'speed': speed
    }

g2 = bs_greeks_full(S=100, K=100, T=30/365, r=0.03, sigma=0.20)
print("ATM 30天 Call 完整 Greeks:")
for k, v in g2.items():
    print(f"  {k:<6}: {v:+.6f}")
