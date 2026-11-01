# @quantlab/output: 64837973
def zcis_fair_rate(expected_cpi_path: np.ndarray,
                    discount_rates: np.ndarray,
                    maturity_years: float) -> float:
    """
    计算零息通胀互换的公平固定利率。

    公平条件：固定端的PV = 通胀端的PV

    参数:
        expected_cpi_path: 预期的CPI指数路径
        discount_rates: 对应期限的贴现率
        maturity_years: 到期年数
    返回:
        零息通胀互换利率 K
    """
    T = int(maturity_years)
    I_0 = expected_cpi_path[0]
    I_T = expected_cpi_path[-1]

    # 通胀端PV
    inflation_pv = (I_T / I_0 - 1) * (1 + discount_rates[-1]) ** (-T)

    # 求解 K 使得固定端PV = 通胀端PV
    # PV_fixed = ((1+K)^T - 1) * DF_T = PV_inflation
    df_T = (1 + discount_rates[-1]) ** (-T)
    K = (inflation_pv / df_T + 1) ** (1 / T) - 1

    return K

# ===== 合成数据最小示例（数据为模拟，机制真实）=====
_cpi_path = np.full(10, 0.024)
_disc = np.full(10, 0.042)
print('10 年期 ZCIS 公平利率:',
      round(zcis_fair_rate(expected_cpi_path=_cpi_path, discount_rates=_disc, maturity_years=10), 4))
