# @quantlab/output: 33c56ecb
def evt_var_es(gpd_params: dict,
               threshold: float,
               n_total: int,
               n_exceedances: int,
               confidence_level: float = 0.99) -> dict:
    """
    基于 EVT (GPD-POT) 的 VaR 和预期亏损估计。

    参数:
        gpd_params: GPD 拟合结果 {'xi': ..., 'beta': ...}
        threshold: POT 阈值 u
        n_total: 总样本量
        n_exceedances: 超过阈值的样本量
        confidence_level: VaR 置信水平
    返回:
        EVT-VaR 和 EVT-ES
    """
    xi = gpd_params['xi']
    beta = gpd_params['beta']
    p = 1 - confidence_level

    # 尾部分布的非参数估计
    zeta_u = n_exceedances / n_total  # 超过阈值比例

    # EVT-VaR: u + β/ξ * [(n/ Nu * p)^{-ξ} - 1]
    if abs(xi) < 1e-8:
        var_evt = threshold - beta * np.log(p / zeta_u)
    else:
        var_evt = threshold + beta / xi * \
            ((p / zeta_u) ** (-xi) - 1)

    # EVT-ES: 预期亏损 = VaR / (1 - ξ) + (β - ξ*u) / (1 - ξ)  (ξ < 1)
    if xi < 1:
        if abs(xi) < 1e-8:
            es_evt = var_evt + beta
        else:
            es_evt = var_evt / (1 - xi) + (beta - xi * threshold) / (1 - xi)
    else:
        es_evt = np.inf  # ξ >= 1 时, ES 无穷大，分布过于厚尾

    return {
        'EVT_VaR': var_evt,
        'EVT_ES': es_evt,
        'gaussian_VaR': threshold + stats.norm.ppf(confidence_level) *
                         np.std(np.random.randn(n_total)),
        'tail_index_xi': xi
    }
