# @quantlab/output: 512292e2
import numpy as np
from scipy.stats import norm

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
    sign = 1 if otype=="call" else -1
    delta = sign * norm.cdf(sign*d1)
    gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
    vega = S*norm.pdf(d1)*np.sqrt(T) / 100
    theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))
             - sign*r*K*np.exp(-r*T)*norm.cdf(d1-sigma*np.sqrt(T)))/365
    return delta, gamma, vega, theta

S, K, T, r, sigma = 100, 100, 30/365, 0.03, 0.20
d_c, g_c, v_c, t_c = greeks(S, K, T, r, sigma, "call")
d_p, g_p, v_p, t_p = greeks(S, K, T, r, sigma, "put")
print(f"Long Straddle Greeks 叠加:")
print(f"  Δ = {d_c+d_p:+.4f}")
print(f"  Γ = {g_c+g_p:+.4f}")
print(f"  ν = {v_c+v_p:+.4f}")
print(f"  Θ = {t_c+t_p:+.4f} (每天)")
print(f"  → Vega 正暴露极强,做多波动率")
