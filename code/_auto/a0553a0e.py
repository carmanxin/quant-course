# @quantlab/output: a0553a0e
def rebalance_decision(P_current, P_lower, P_upper, gas_cost_eth, position_value_eth):
    """
    判断是否应该进行再平衡
    """
    range_width = (P_upper - P_lower) / ((P_upper + P_lower) / 2)

    # 价格接近区间边界的阈值
    rebalance_threshold_low = P_lower * 1.05  # 价格在5%内触及下限
    rebalance_threshold_high = P_upper * 0.95  # 价格在5%内触及上限

    if P_current <= rebalance_threshold_low or P_current >= rebalance_threshold_high:
        # 评估再平衡成本 vs 收益
        # 退出成本 = gas 费用
        exit_cost = gas_cost_eth * 2  # 退出 + 重新进入

        # 停留在原区间的预期损失
        if P_current <= P_lower:
            expected_loss_out_of_range = position_value_eth
        else:
            expected_loss_out_of_range = 0

        # 再平衡决策
        rebalance = expected_loss_out_of_range > exit_cost * 5  # 5倍收益/成本比
        return {
            'should_rebalance': rebalance,
            'reason': f"价格 {P_current:.2f} 接近{'下限' if P_current <= rebalance_threshold_low else '上限'}",
            'estimated_gas_cost_eth': exit_cost
        }

    return {'should_rebalance': False, 'reason': '价格在合理区间内'}
