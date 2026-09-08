# @quantlab/output: b2e021d2
def constraint_impact_analysis(mu, Sigma, benchmark_weights=None):
    """
    分析不同约束条件对组合的影响

    依次添加约束，观察权重和绩效的变化
    """
    configs = [
        {'name': '无约束', 'long_only': False, 'max_weight': 1.0},
        {'name': '仅做多', 'long_only': True, 'max_weight': 1.0},
        {'name': '做多+上限10%', 'long_only': True, 'max_weight': 0.1},
        {'name': '做多+上限5%', 'long_only': True, 'max_weight': 0.05},
    ]

    optimizer = PortfolioOptimizerWithConstraints(mu, Sigma, benchmark_weights)
    results = []

    for cfg in configs:
        w = optimizer.optimize(objective_type='min_variance', config=cfg)
        port_vol = np.sqrt(w @ Sigma @ w)
        port_ret = w @ mu
        n_stocks = (w > 0.001).sum()  # 有效持仓数
        effective_n = 1 / np.sum(w ** 2)  # 有效分散度

        results.append({
            '约束': cfg['name'],
            '年化收益': f'{port_ret*252:.1%}',
            '年化波动': f'{port_vol*np.sqrt(252):.1%}',
            '持仓数量': n_stocks,
            '有效分散度': f'{effective_n:.1f}',
            '最大权重': f'{w.max():.1%}',
        })

    return pd.DataFrame(results)
