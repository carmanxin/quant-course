# @quantlab/output: c918e249
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
