# @quantlab/output: 062553f7
def refi_incentive_model(wac, current_rate, base_cpr, refi_sensitivity=0.3):
    """
    考虑再融资激励的提前还款模型
    wac: 贷款加权平均票面利率
    current_rate: 当前市场利率
    base_cpr: 基准CPR（再融资无激励时）
    refi_sensitivity: 再融资弹性
    """
    rate_spread = wac - current_rate
    if rate_spread > 0:
        # 再融资激励存在，CPR上升
        refi_multiplier = 1 + refi_sensitivity * rate_spread * 100
    else:
        refi_multiplier = 1.0

    cpr = base_cpr * refi_multiplier
    return min(cpr, 0.60)  # CPR 上限 60%
