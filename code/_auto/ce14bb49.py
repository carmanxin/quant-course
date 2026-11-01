# @quantlab/output: ce14bb49
import numpy as np
from scipy.stats import norm

# 获取 50ETF 期权实时行情与 Greeks (使用 akshare)
# pip install akshare
import akshare as ak

# 假设已获取 50ETF 期权 T型报价
# 实际接口: ak.option_sse_50etf_spot_em() 或东方财富 akshare 接口
S_spot = 2.800  # 50ETF 现价
K_atm = 2.800
T = 30 / 365
r = 0.025
sigma = 0.20  # 隐含波动率

def bs_greeks(S, K, T, r, sigma, otype="call"):
    d1 = (np.log(S/K) + (r+sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    sign = 1 if otype=="call" else -1
    delta = sign * norm.cdf(sign*d1)
    gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
    vega = S*norm.pdf(d1)*np.sqrt(T) / 100
    theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))
             - sign*r*K*np.exp(-r*T)*norm.cdf(sign*d2))/365
    return delta, gamma, vega, theta

print(f"\n{'类型':>6} {'行权价':>8} {'Delta':>8} {'Gamma':>8} {'Vega':>8} {'Theta/日':>10}")
for otype, K in [("call",2.700),("call",2.800),("call",2.900),
                 ("put",2.700),("put",2.800),("put",2.900)]:
    d,g,v,t = bs_greeks(S_spot,K,T,r,sigma,otype)
    print(f"{otype:>6} {K:8.3f} {d:+8.4f} {g:8.4f} {v:8.4f} {t:+10.4f}")
