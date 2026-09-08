# @quantlab/output: 1ffccec3
def macro_regime_factor_allocation(macro_state: str,
                                    factor_universe: dict) -> dict:
    """
    基于宏观状态的因子配置权重。

    参数:
        macro_state: 宏观状态标签
            - 'expansion': 扩张期
            - 'contraction': 收缩期
            - 'stagflation': 滞胀期
            - 'recovery': 复苏期
        factor_universe: 因子名称到中性权重的映射
    返回:
        调整后的因子权重
    """
    # 宏观状态与因子表现的关系矩阵
    regime_tilts = {
        'expansion': {'momentum': 1.5, 'growth': 1.5, 'quality': 1.0,
                       'value': 0.5, 'low_vol': 0.5, 'size': 1.0},
        'contraction': {'momentum': 0.5, 'growth': 0.3, 'quality': 2.0,
                         'value': 0.8, 'low_vol': 2.0, 'size': 0.2},
        'stagflation': {'momentum': 0.5, 'growth': 0.2, 'quality': 1.0,
                         'value': 1.5, 'low_vol': 1.0, 'size': 0.5},
        'recovery': {'momentum': 1.0, 'growth': 1.2, 'quality': 1.0,
                      'value': 1.5, 'low_vol': 0.5, 'size': 1.8}
    }

    if macro_state not in regime_tilts:
        return factor_universe  # 未知状态，保持中性

    tilts = regime_tilts[macro_state]

    # 计算调整后的权重
    adjusted_weights = {}
    for factor, neutral_weight in factor_universe.items():
        tilt = tilts.get(factor, 1.0)
        adjusted_weights[factor] = neutral_weight * tilt

    # 归一化
    total = sum(adjusted_weights.values())
    adjusted_weights = {k: v / total for k, v in adjusted_weights.items()}

    return adjusted_weights
