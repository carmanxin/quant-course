# @quantlab/output: 2336173c
def reverse_stress_test(positions_sensitivities: np.ndarray,
                         max_acceptable_loss: float,
                         factor_bounds: list,
                         n_search: int = 10000) -> dict:
    """
    逆向压力测试：找出导致给定损失的最小因子冲击组合。

    优化问题：min ||Δf||_2, s.t. P&L(Δf) ≤ -max_acceptable_loss

    参数:
        positions_sensitivities: (M,) 对各风险因子的敏感度向量
        max_acceptable_loss: 最大可接受损失（正值）
        factor_bounds: [(min, max), ...] 各因子的合理变动范围
        n_search: 搜索次数
    返回:
        最小范数冲击组合及其 P&L
    """
    M = len(positions_sensitivities)

    best_shock = None
    best_norm = np.inf

    for _ in range(n_search):
        # 随机生成因子冲击（在各因子的边界内均匀采样）
        shocks = np.array([
            np.random.uniform(low, high) for low, high in factor_bounds
        ])

        # 计算 P&L
        pnl = np.dot(positions_sensitivities, shocks)

        if pnl <= -max_acceptable_loss:
            norm = np.linalg.norm(shocks, 2)
            if norm < best_norm:
                best_norm = norm
                best_shock = shocks.copy()

    if best_shock is None:
        return {'found': False, 'message': '在搜索范围内未找到符合条件的冲击组合'}

    return {
        'found': True,
        'shocks': best_shock,
        'shock_norm': best_norm,
        'resulting_pnl': np.dot(positions_sensitivities, best_shock),
        'normalized_shocks': best_shock / np.linalg.norm(best_shock)
    }
