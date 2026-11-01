# @quantlab/output: d853fe5e
def mvo_sensitivity_cov(returns, n_simulations=100, noise_level=0.1):
    """
    分析协方差矩阵估计误差对MVO权重的影响

    对协方差矩阵加入随机噪声，观察权重的分布
    """
    mu = returns.mean() * 252
    Sigma = returns.cov() * 252
    n = len(mu)

    weight_distribution = np.zeros((n_simulations, n))

    for i in range(n_simulations):
        # 对协方差矩阵加噪声
        noise = np.random.normal(0, noise_level, Sigma.shape)
        noise = (noise + noise.T) / 2  # 保持对称
        np.fill_diagonal(noise, np.diag(noise) * 2)  # 对角线加更多噪声

        Sigma_noisy = Sigma * (1 + noise)

        try:
            w = mvo_min_variance(mu, Sigma_noisy)
            weight_distribution[i] = w
        except Exception:
            continue

    # 分析权重的不确定性
    mean_weights = weight_distribution.mean(axis=0)
    std_weights = weight_distribution.std(axis=0)

    print(f"权重不确定性的均值: {std_weights.mean():.4f}")
    print(f"最不确定的资产: std={std_weights.max():.4f}")

    return mean_weights, std_weights
