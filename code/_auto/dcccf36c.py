# @quantlab/output: dcccf36c
def estimate_kyle_lambda(price_changes: np.ndarray,
                          signed_volume: np.ndarray) -> dict:
    """
    通过回归估计 Kyle's Lambda。

    回归方程: Δp_t = λ · Q_t + ε_t
    其中 Q_t 是带符号的成交量（买方为正，卖方为负）。

    参数:
        price_changes: 价格变动序列
        signed_volume: 带符号成交量序列
    返回:
        包含 lambda_estimate, r_squared, t_stat 的字典
    """
    from scipy import stats

    # 添加截距项
    X = np.column_stack([np.ones(len(signed_volume)), signed_volume])
    y = price_changes

    # OLS 回归
    beta = np.linalg.inv(X.T @ X) @ X.T @ y
    lambda_hat = beta[1]

    # 拟合值与残差
    y_pred = X @ beta
    residuals = y - y_pred

    # R²
    ss_total = np.sum((y - np.mean(y)) ** 2)
    ss_residual = np.sum(residuals ** 2)
    r_squared = 1 - ss_residual / ss_total

    # t 统计量
    n = len(y)
    se = np.sqrt(ss_residual / (n - 2) / np.sum((signed_volume - np.mean(signed_volume)) ** 2))
    t_stat = lambda_hat / se

    return {
        'lambda_estimate': lambda_hat,
        'r_squared': r_squared,
        't_stat': t_stat,
        'significant': abs(t_stat) > 1.96
    }
