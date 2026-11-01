# @quantlab/output: ae639efd
def compute_pbo(returns, n_trials=100, test_size=0.5):
    """
    使用组合对称交叉验证(CSCV)计算PBO

    Parameters:
        returns: T x K matrix, K个策略变体在T个时间点的收益率
    """
    T, K = returns.shape
    n_test = int(T * test_size)
    n_train = T - n_test

    is_ranks = []
    oos_ranks = []

    for _ in range(n_trials):
        # 随机划分训练/测试集
        idx = np.random.permutation(T)
        train_idx = idx[:n_train]
        test_idx = idx[n_train:]

        # 计算样本内夏普
        is_sharpe = returns[train_idx].mean(axis=0) / returns[train_idx].std(axis=0) * np.sqrt(252)
        # 计算样本外夏普
        oos_sharpe = returns[test_idx].mean(axis=0) / returns[test_idx].std(axis=0) * np.sqrt(252)

        # 找出样本内最优策略
        best_is_idx = np.argmax(is_sharpe)

        # 排名（归一化到[0,1]）
        is_rank = (np.sum(is_sharpe <= is_sharpe[best_is_idx]) - 1) / (K - 1) if K > 1 else 0.5
        oos_rank = np.sum(oos_sharpe <= oos_sharpe[best_is_idx]) / K

        is_ranks.append(is_rank)
        oos_ranks.append(oos_rank)

    # PBO = 样本内排名 > 1 - 样本外排名的频率
    is_ranks = np.array(is_ranks)
    oos_ranks = np.array(oos_ranks)
    pbo = np.mean(is_ranks >= (1 - oos_ranks))

    print(f"PBO: {pbo:.4f}")
    if pbo > 0.5:
        print("⚠️ 过拟合风险较高！样本内最优策略在样本外倾向于表现最差。")
    else:
        print("✅ 过拟合风险可控。样本内最优策略在样本外也有较好的相对排名。")

    return pbo
