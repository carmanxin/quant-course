# @quantlab/output: ffaa4f10
def simple_dcc_estimate(returns_1: np.ndarray,
                         returns_2: np.ndarray,
                         half_life: int = 20) -> np.ndarray:
    """
    简化的动态条件相关性估计（指数加权移动平均）。

    DCC_t = q12_t / sqrt(q11_t * q22_t)

    参数:
        returns_1, returns_2: 两个资产的收益率
        half_life: EWMA半衰期（天）
    返回:
        时变相关性序列
    """
    alpha = 2.0 / (half_life + 1)  # EWMA衰减因子

    T = len(returns_1)
    q11 = np.zeros(T)
    q22 = np.zeros(T)
    q12 = np.zeros(T)
    dcc = np.zeros(T)

    # 初始化：无条件方差/协方差
    q11[0] = np.var(returns_1)
    q22[0] = np.var(returns_2)
    q12[0] = np.cov(returns_1, returns_2)[0, 1]

    for t in range(1, T):
        q11[t] = (1 - alpha) * q11[t-1] + alpha * returns_1[t-1] ** 2
        q22[t] = (1 - alpha) * q22[t-1] + alpha * returns_2[t-1] ** 2
        q12[t] = (1 - alpha) * q12[t-1] + alpha * returns_1[t-1] * returns_2[t-1]

        dcc[t] = q12[t] / (np.sqrt(q11[t]) * np.sqrt(q22[t]) + 1e-10)

    return dcc
