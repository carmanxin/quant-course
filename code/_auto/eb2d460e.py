# @quantlab/output: eb2d460e
def multi_asset_mc(S0_vec, K, T, r, sigma_vec, corr_matrix, n_paths):
    """
    多资产篮子期权蒙特卡洛定价
    S0_vec: 各资产的初始价格
    sigma_vec: 各资产的波动率
    corr_matrix: 相关系数矩阵
    """
    n_assets = len(S0_vec)
    L = np.linalg.cholesky(corr_matrix)  # Cholesky 下三角矩阵

    Z_independent = np.random.randn(n_paths, n_assets)
    Z_correlated = Z_independent @ L.T  # 生成相关的随机变量

    ST = np.zeros((n_paths, n_assets))
    for i in range(n_assets):
        ST[:, i] = S0_vec[i] * np.exp(
            (r - 0.5*sigma_vec[i]**2)*T
            + sigma_vec[i]*np.sqrt(T)*Z_correlated[:, i]
        )

    # 一篮子看涨期权
    basket_avg = ST.mean(axis=1)
    payoff = np.maximum(basket_avg - K, 0)
    price = np.exp(-r * T) * payoff.mean()

    return price
