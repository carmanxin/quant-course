# @quantlab/output: 2.2-black-scholes
import numpy as np
from scipy.stats import norm
def black_scholes(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    call = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    return call
call_price = black_scholes(100, 105, 0.5, 0.03, 0.2)
print(f'看涨期权价格: ${call_price:.4f}')
