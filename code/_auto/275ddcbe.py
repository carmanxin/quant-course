# @quantlab/output: 275ddcbe
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# 示例：从市场上观测到的债券价格 bootstrapping 即期曲线
def bootstrap_spot_curve(bonds):
    """
    bonds: list of dicts with keys 'maturity', 'coupon', 'price'
    使用 bootstrapping 方法从附息债券价格中提取即期利率曲线
    """
    bonds = sorted(bonds, key=lambda x: x['maturity'])
    spot_rates = []
    maturities = []

    for i, bond in enumerate(bonds):
        T = bond['maturity']
        coupon = bond['coupon'] / 2  # 半年付息
        price = bond['price']
        n_payments = int(T * 2)

        if T <= 0.5:
            # 短端直接用零息公式
            r = -np.log(price / (100 + coupon)) / T
        else:
            # 使用已求出的即期利率折现前面的现金流
            pv_coupons = 0
            for j in range(1, n_payments):
                t_j = j * 0.5
                if t_j <= maturities[-1]:
                    # 有对应的即期利率
                    idx = np.searchsorted(maturities, t_j)
                    if idx < len(spot_rates):
                        r_spot = spot_rates[idx]
                    else:
                        r_spot = spot_rates[-1]
                    pv_coupons += coupon * np.exp(-r_spot * t_j)
                else:
                    # 需要插值
                    cs = CubicSpline(maturities, spot_rates)
                    r_interp = cs(t_j)
                    pv_coupons += coupon * np.exp(-r_interp * t_j)

            r = -np.log((price - pv_coupons) / (100 + coupon)) / T

        spot_rates.append(r)
        maturities.append(T)

    return np.array(maturities), np.array(spot_rates)
