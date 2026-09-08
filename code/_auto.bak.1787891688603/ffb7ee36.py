# @quantlab/output: ffb7ee36
def inflation_hedge_portfolio(inflation_regime: str,
                               risk_budget: float = 0.10) -> dict:
    """
    基于通胀环境构建对冲组合。

    参数:
        inflation_regime: 通胀环境
            - 'rising': 通胀上升
            - 'falling': 通胀下降/通缩
            - 'stable_high': 高通胀但稳定
            - 'stable_low': 低通胀且稳定
        risk_budget: 分配给通胀对冲的风险预算
    返回:
        对冲组合的资产配置权重
    """
    # 各资产在不同通胀环境下的配置权重
    hedge_allocation = {
        'rising': {
            'TIPS': 0.30, '黄金': 0.15, '商品期货': 0.20,
            '大宗商品股票': 0.15, '浮动利率债券': 0.10,
            'REITs': 0.05, '现金': 0.05
        },
        'falling': {
            '名义长期国债': 0.40, '投资级公司债': 0.25,
            '成长股': 0.15, 'TIPS': 0.10, '现金': 0.10
        },
        'stable_high': {
            'TIPS': 0.25, 'REITs': 0.20, '价值股': 0.15,
            '基础设施': 0.15, '商品': 0.10, '浮动利率债券': 0.15
        },
        'stable_low': {
            '名义国债': 0.20, '投资级公司债': 0.25,
            '成长股': 0.30, '高质量股利股': 0.15, 'TIPS': 0.10
        }
    }

    # 获取对应配置
    weights = hedge_allocation.get(inflation_regime,
                                    hedge_allocation['stable_low'])

    # 按风险预算缩放
    scaled_weights = {k: v * risk_budget for k, v in weights.items()}

    return scaled_weights
