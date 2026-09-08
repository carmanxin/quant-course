# @quantlab/output: 0c67eac2
def calculate_basel_capital_ratios(cet1: float,
                                    tier1: float,
                                    total_capital: float,
                                    rwa_credit: float,
                                    rwa_market: float,
                                    rwa_operational: float,
                                    total_exposure: float,
                                    is_gsib: bool = False) -> dict:
    """
    计算 Basel III 资本充足率指标。

    参数:
        cet1: 核心一级资本
        tier1: 一级资本
        total_capital: 总资本（Tier1+Tier2）
        rwa_credit: 信用风险加权资产
        rwa_market: 市场风险加权资产
        rwa_operational: 操作风险加权资产
        total_exposure: 杠杆率分母（总暴露）
        is_gsib: 是否为全球系统重要性银行
    返回:
        各比率及其与最低要求的比较
    """
    total_rwa = rwa_credit + rwa_market + rwa_operational

    cet1_ratio = cet1 / total_rwa * 100
    tier1_ratio = tier1 / total_rwa * 100
    total_capital_ratio = total_capital / total_rwa * 100
    leverage_ratio = cet1 / total_exposure * 100

    # 最低要求（含缓冲）
    min_cet1 = 4.5 + 2.5  # +CCB
    min_tier1 = 6.0 + 2.5
    min_total = 8.0 + 2.5
    min_leverage = 3.0

    if is_gsib:
        gsib_surcharge = 2.0  # 简化假设
        min_cet1 += gsib_surcharge
        min_tier1 += gsib_surcharge
        min_total += gsib_surcharge

    return {
        'CET1_Ratio': cet1_ratio,
        'CET1_Minimum': min_cet1,
        'CET1_Headroom': cet1_ratio - min_cet1,
        'Tier1_Ratio': tier1_ratio,
        'Tier1_Minimum': min_tier1,
        'Tier1_Headroom': tier1_ratio - min_tier1,
        'Total_Capital_Ratio': total_capital_ratio,
        'Total_Capital_Minimum': min_total,
        'Leverage_Ratio': leverage_ratio,
        'Leverage_Minimum': min_leverage,
        'Compliant': (
            cet1_ratio >= min_cet1 and
            tier1_ratio >= min_tier1 and
            total_capital_ratio >= min_total and
            leverage_ratio >= min_leverage
        )
    }
