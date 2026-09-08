# @quantlab/output: 102da2d7
def market_risk_standardized_approach(positions: dict,
                                       sensitivities: dict,
                                       risk_weights: dict) -> dict:
    """
    简化版市场风险标准法（SA）的资本计算。

    基于敏感度的方法（Sensitivities-Based Method）：
    1. 计算各风险因子的敏感度
    2. 应用监管风险权重
    3. 按风险类别聚合
    4. 跨类别相关聚合

    参数:
        positions: {头寸ID: 名义本金}
        sensitivities: {头寸ID: {风险因子: 敏感度}}
        risk_weights: {风险因子: 监管风险权重}
    返回:
        市场风险 RWA
    """
    # 风险类别分组
    risk_classes = {
        'GIRR': ['rate_1y', 'rate_5y', 'rate_10y', 'rate_30y'],
        'CSR': ['credit_AAA', 'credit_BBB', 'credit_HY'],
        'Equity': ['equity_large_cap', 'equity_small_cap',
                    'equity_emerging'],
        'FX': ['fx_eur', 'fx_jpy', 'fx_gbp', 'fx_em'],
        'Commodity': ['commodity_energy', 'commodity_metals',
                       'commodity_agriculture']
    }

    # 步骤1：计算加权敏感度
    weighted_sensitivities = {cls: np.zeros(len(factors))
                               for cls, factors in risk_classes.items()}

    for position_id, nominal in positions.items():
        for factor, sensitivity in sensitivities.get(position_id, {}).items():
            for cls, factors in risk_classes.items():
                if factor in factors:
                    idx = factors.index(factor)
                    weight = risk_weights.get(factor, 0.05)
                    weighted_sensitivities[cls][idx] += \
                        nominal * sensitivity * weight

    # 步骤2：按风险类别内聚合
    # 类内相关系数矩阵
    rho_intra = {
        'GIRR': 0.5, 'CSR': 0.4, 'Equity': 0.6,
        'FX': 0.5, 'Commodity': 0.4
    }

    class_capital = {}
    for cls, ws in weighted_sensitivities.items():
        K = len(ws)
        if K <= 1:
            class_capital[cls] = abs(ws[0]) if K == 1 else 0
        else:
            # 有相关聚合
            sum_sq = np.sum(ws ** 2)
            sum_cross = 0
            for i in range(K):
                for j in range(K):
                    if i != j:
                        sum_cross += ws[i] * ws[j] * rho_intra[cls]
            class_capital[cls] = np.sqrt(max(sum_sq + sum_cross, 0))

    # 步骤3：跨风险类别聚合（类间相关系数 = 0.5）
    rho_inter = 0.5
    total_capital = np.sqrt(
        sum(v**2 for v in class_capital.values()) +
        sum(class_capital[c1] * class_capital[c2] * rho_inter
            for i, c1 in enumerate(class_capital)
            for c2 in list(class_capital.keys())[i+1:])
    )

    # 步骤4：RWA = 资本要求 * 12.5（8% 最低资本比率的倒数）
    rwa = total_capital * 12.5

    return {
        'Class_Capitals': class_capital,
        'Total_Capital_Charge': total_capital,
        'Market_Risk_RWA': rwa,
        'Implied_Min_Capital': rwa * 0.08
    }
