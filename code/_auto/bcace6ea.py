# @quantlab/output: bcace6ea
def bs_call(S, K, T, r, sigma):
    if T <= 0:
        return max(S-K, 0)
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)

def implied_vol(market_price, S, K, T, r, sigma_init=0.2):
    """牛顿迭代反推隐含波动率"""
    sigma = sigma_init
    for i in range(100):
        bs_val = bs_call(S, K, T, r, sigma)
        diff = bs_val - market_price
        if abs(diff) < 1e-6:
            return sigma
        # Vega 解析
        d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
        vega = S*np.exp(-d1**2/2)/np.sqrt(2*np.pi)*np.sqrt(T)
        sigma -= diff/vega
        if sigma <= 0:
            sigma = 0.001
    return sigma

# 示例
S, K, T, r = 100, 100, 0.5, 0.03
opt_market = 4.5
iv = implied_vol(opt_market, S, K, T, r)
print(f"市价 {opt_market} 对应的隐含波动率: {iv*100:.2f}%")
