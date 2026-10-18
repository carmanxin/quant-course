# @quantlab/output: 0578730b
def generate_extreme_scenarios(n_scenarios=1000, base_mu=0.0005, base_sigma=0.01):
    """
    使用参数化方法生成极端市场场景用于压力测试

    该方法利用Copula + 尾部依赖来生成多资产极端共跌场景
    """
    from scipy.stats import norm, t as t_dist

    results = []

    for i in range(n_scenarios):
        # 生成相关性矩阵（随机但保持正定性）
        n_assets = 5
        random_corr = np.random.uniform(0.3, 0.8, size=(n_assets, n_assets))
        random_corr = (random_corr + random_corr.T) / 2
        np.fill_diagonal(random_corr, 1.0)

        try:
            L = np.linalg.cholesky(random_corr)
        except np.linalg.LinAlgError:
            continue

        # 使用t-Copula（胖尾）生成联合场景
        df = 3  # 自由度=3，尾部很厚
        z = np.random.randn(n_assets)
        u = L @ z

        # t分布缩放（引入共线性极端事件）
        chi = np.random.chisquare(df) / df
        scenarios = u / np.sqrt(chi) * base_sigma * 3  # 3倍波动

        results.append({
            'scenario_id': i,
            'returns': scenarios,
            'max_loss': scenarios.min(),
            'correlation': random_corr[0, 1],
            'total_shock': np.abs(scenarios).sum()
        })

    # 找出Top 10最极端的场景
    results.sort(key=lambda x: x['total_shock'], reverse=True)

    print("极端场景压力测试:")
    print("-" * 50)
    for i, r in enumerate(results[:5]):
        print(f"场景 {r['scenario_id']}: 最大跌幅={r['max_loss']:.2%}, "
              f"总冲击={r['total_shock']:.2%}")

    return results

extreme_scenarios = generate_extreme_scenarios(500)
