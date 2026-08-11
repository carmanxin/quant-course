import numpy as np
from scipy.stats import norm
def bs_greeks(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = (-S * norm.pdf(d1) * sigma / (2*np.sqrt(T)) - r*K*np.exp(-r*T)*norm.cdf(d2)) / 365
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    rho = K * T * np.exp(-r*T) * norm.cdf(d2) / 100
    return delta, gamma, theta, vega, rho
S, K, T, r, sigma = 100, 100, 0.5, 0.03, 0.2
delta, gamma, theta, vega, rho = bs_greeks(S, K, T, r, sigma)
print(f'标的价: {S}, 行权价: {K}, 期限: {T}年')
print(f'Delta : {delta:.4f}  (标的价格变动1元，期权价格变动)')
print(f'Gamma : {gamma:.4f}  (标的价格变动1元，Delta变动)')
print(f'Theta : {theta:.4f}  (每过1天，期权价值衰减)')
print(f'Vega  : {vega:.4f}  (波动率变动1%，期权价格变动)')
print(f'Rho   : {rho:.4f}  (利率变动1%，期权价格变动)')
