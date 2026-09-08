# @quantlab/output: 67916a3c
import numpy as np

def irs_pricing(notional, fixed_rate, float_spread, payment_dates,
                discount_factors, float_rates, is_payer=True):
    """
    利率互换定价
    notional: 名义本金
    fixed_rate: 固定端利率
    float_spread: 浮动端利差
    payment_dates: 支付日列表（年化）
    discount_factors: 对应的折现因子
    float_rates: 各期的浮动参考利率（远期利率）
    is_payer: True=支付固定收取浮动; False=收取固定支付浮动
    """
    dt = np.diff([0] + list(payment_dates))

    # 固定端现值
    fixed_pv = 0
    for i, (t, df) in enumerate(zip(payment_dates, discount_factors)):
        fixed_pv += notional * fixed_rate * dt[i] * df

    # 浮动端现值
    float_pv = 0
    for i, (t, df, fwd) in enumerate(zip(payment_dates, discount_factors, float_rates)):
        float_pv += notional * (fwd + float_spread) * dt[i] * df

    sign = -1 if is_payer else 1
    swap_value = sign * (float_pv - fixed_pv)
    return swap_value, fixed_pv, float_pv
