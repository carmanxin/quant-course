# @quantlab/output: d6ea1aef
def immunize_single_liability(liability, liability_time, bonds, ytm):
    """
    对单一负债进行免疫
    liability: 负债金额
    liability_time: 负债到期时间（年）
    bonds: list of dicts with 'duration', 'price', 'convexity'
    """
    # 计算负债的现值和久期
    pv_liability = liability / (1 + ytm) ** liability_time

    print(f"负债现值: {pv_liability:,.2f}")
    print(f"负债久期: {liability_time:.2f} 年")

    # 目标：找到两个债券的权重使组合久期等于负债久期
    # w1 * D1 + w2 * D2 = D_liability
    # w1 + w2 = 1
    D1, D2 = bonds[0]['duration'], bonds[1]['duration']
    w1 = (liability_time - D2) / (D1 - D2)
    w2 = 1 - w1

    # 计算需要购买的金额
    amount_bond1 = pv_liability * w1
    amount_bond2 = pv_liability * w2

    return {
        'bond1_allocation': amount_bond1,
        'bond2_allocation': amount_bond2,
        'portfolio_duration': w1 * D1 + w2 * D2
    }
