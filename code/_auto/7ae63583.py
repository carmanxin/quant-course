# @quantlab/output: 7ae63583
from scipy.stats import norm

def black_swaption(forward_swap_rate, strike, annuity, T, sigma, swaption_type='payer'):
    """
    Black's model 互换期权定价
    forward_swap_rate: 远期互换利率 F
    strike: 行权利率 K
    annuity: 年金因子 A（现值基点）
    T: 期权到期时间（年）
    sigma: 互换利率的波动率
    """
    if T <= 0:
        payoff = max(0, forward_swap_rate - strike) if swaption_type == 'payer' \
            else max(0, strike - forward_swap_rate)
        return payoff * annuity

    d1 = (np.log(forward_swap_rate / strike) + 0.5 * sigma**2 * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if swaption_type == 'payer':
        price = annuity * (forward_swap_rate * norm.cdf(d1) - strike * norm.cdf(d2))
    else:
        price = annuity * (strike * norm.cdf(-d2) - forward_swap_rate * norm.cdf(-d1))

    return price

# 示例：1Y-into-5Y Payer Swaption
forward_swap = 0.035     # 1年后开始的5年期远期互换利率
strike = 0.035            # ATM
annuity = 4.5             # 5年期年金的现值基点（近似）
T_option = 1.0            # 1年后期权到期
vol = 0.20                # 20% 波动率

price = black_swaption(forward_swap, strike, annuity, T_option, vol, 'payer')
print(f"Payer Swaption 价格 (bps): {price * 10000:.2f}")
