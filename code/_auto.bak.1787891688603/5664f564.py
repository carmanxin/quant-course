# @quantlab/output: 5664f564
def comprehensive_hedge(portfolio, hedge_instruments, scenarios):
    """
    全面利率风险对冲
    portfolio: 被对冲组合的希腊字母 {DV01_bucket: value}
    hedge_instruments: 可用的对冲工具 [{'name': ..., 'dv01': ..., 'vega': ...}]
    scenarios: 考虑的风险情景
    """
    # 构建希腊字母矩阵
    n_hedge = len(hedge_instruments)
    n_risks = len(scenarios)

    # 风险矩阵：每行是一种对冲工具对不同情景的敏感度
    risk_matrix = np.zeros((n_risks, n_hedge))
    portfolio_risk = np.zeros(n_risks)

    for j, inst in enumerate(hedge_instruments):
        for i, scenario in enumerate(scenarios):
            risk_matrix[i, j] = scenario['impact'](inst)

    for i, scenario in enumerate(scenarios):
        portfolio_risk[i] = -scenario['impact_on_portfolio'](portfolio)

    # 最小二乘求解对冲比例
    weights = np.linalg.lstsq(risk_matrix, portfolio_risk, rcond=None)[0]

    return dict(zip([h['name'] for h in hedge_instruments], weights))
