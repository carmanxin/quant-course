# @quantlab/output: 361643e6
def stress_test_portfolio(weights, factor_sensitivities, scenarios):
    """
    对投资组合进行多情景压力测试

    Parameters:
        weights: 资产权重向量 (N,)
        factor_sensitivities: 各资产对各风险因子的敏感度 (N, K)
        scenarios: dict, {scenario_name: {factor_name: shock}}
            shock: 因子变化（如利率+100bp, 指数-20%）
    """
    results = {}

    for scenario_name, shocks in scenarios.items():
        # 将情景冲击转换为每个资产的收益冲击
        asset_shocks = np.zeros(len(weights))
        for factor_name, shock in shocks.items():
            if factor_name in factor_sensitivities.columns:
                asset_shocks += factor_sensitivities[factor_name] * shock

        # 组合层面的损失
        portfolio_loss = -np.sum(weights * asset_shocks)
        results[scenario_name] = portfolio_loss

    return pd.Series(results, name='Portfolio Loss')

# 定义压力情景
scenarios = {
    '2008金融危机': {
        'equity': -0.45,      # 股票跌45%
        'credit_spread': 0.05,  # 信用利差扩大5%
        'volatility': 0.40,    # 波动率上升40%
        'liquidity': -0.30,    # 流动性下降30%
    },
    '2020新冠崩盘': {
        'equity': -0.34,
        'credit_spread': 0.03,
        'volatility': 0.50,
        'liquidity': -0.20,
    },
    '利率急升': {
        'equity': -0.15,
        'interest_rate': 0.02,  # 利率+200bp
        'credit_spread': 0.01,
    },
    '通胀飙升': {
        'equity': -0.10,
        'commodity': 0.20,
        'interest_rate': 0.025,
        'volatility': 0.15,
    },
    '自定极端': {
        'equity': -0.30,
        'credit_spread': 0.05,
        'volatility': 0.40,
        'liquidity': -0.40,
        'interest_rate': 0.03,
    }
}
