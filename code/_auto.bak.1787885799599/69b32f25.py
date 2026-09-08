# @quantlab/output: 69b32f25
def hill_estimator(sorted_losses: np.ndarray,
                    k_values: list = None) -> pd.DataFrame:
    """
    Hill 估计量用于估计尾部指数。

    参数:
        sorted_losses: 降序排列的损失数据
        k_values: 用于估计的极端次序统计量数量列表
    返回:
        各 k 下的尾部指数估计 DataFrame
    """
    n = len(sorted_losses)
    if k_values is None:
        k_values = range(10, min(500, n // 10))

    results = []
    for k in k_values:
        if k >= n or k < 2:
            continue

        # Hill 估计量
        X_k_plus_1 = sorted_losses[k]  # 第 k+1 个次序统计量
        sum_log_ratio = np.sum(np.log(sorted_losses[:k] / X_k_plus_1))
        alpha_hat = k / sum_log_ratio
        xi_hat = 1.0 / alpha_hat

        # 近似标准误
        se_xi = xi_hat / np.sqrt(k)

        results.append({
            'k': k,
            'alpha': alpha_hat,
            'xi': xi_hat,
            'se_xi': se_xi,
            'xi_lower': xi_hat - 1.96 * se_xi,
            'xi_upper': xi_hat + 1.96 * se_xi
        })

    df = pd.DataFrame(results)

    # 绘制 Hill 图
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(df['k'], df['xi'], 'b-', linewidth=1)
    axes[0].fill_between(df['k'], df['xi_lower'], df['xi_upper'],
                          alpha=0.3, color='blue')
    axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('k (极端次序统计量数量)')
    axes[0].set_ylabel('尾部指数 ξ')
    axes[0].set_title('Hill 估计量: 尾部指数 vs 次序统计量')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(df['k'], df['alpha'], 'r-', linewidth=1)
    axes[1].set_xlabel('k (极端次序统计量数量)')
    axes[1].set_ylabel('尾部指数 α = 1/ξ')
    axes[1].set_title('Hill 估计量: α vs 次序统计量')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    return df
