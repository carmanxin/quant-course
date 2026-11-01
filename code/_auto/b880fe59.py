# @quantlab/output: b880fe59
def cross_asset_linkage(fx_changes: np.ndarray,
                         rate_changes: np.ndarray,
                         commodity_changes: np.ndarray,
                         window: int = 60) -> pd.DataFrame:
    """
    量化汇率、利率、大宗商品之间的联动关系。

    使用VAR模型估计相互影响。

    参数:
        fx_changes: 汇率变动率
        rate_changes: 利率变动（收益率变动）
        commodity_changes: 大宗商品价格变动率
        window: 滚动窗口
    返回:
        滚动回归系数DataFrame
    """
    T = len(fx_changes)

    results = []
    for t in range(window, T):
        # 局部数据
        fx = fx_changes[t-window:t]
        rate = rate_changes[t-window:t]
        comm = commodity_changes[t-window:t]

        # 回归: ΔFX = α + β1 * ΔRates + β2 * ΔCommodity + ε
        X = np.column_stack([np.ones(window), rate, comm])
        y = fx

        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        results.append({
            'date': t,
            'constant': beta[0],
            'beta_rate': beta[1],
            'beta_commodity': beta[2],
            'r_squared': 1 - np.sum((y - X @ beta) ** 2) / np.sum((y - np.mean(y)) ** 2)
        })

    return pd.DataFrame(results)
