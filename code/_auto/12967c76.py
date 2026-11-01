# @quantlab/output: 12967c76
# 三明治攻击的简化模型
def sandwich_attack_model(victim_trade_size, pool_liquidity, gas_cost, slippage=0.003):
    """
    三明治攻击的盈利模型
    victim_trade_size: 受害者交易规模（以基础资产计）
    pool_liquidity: AMM 池的总流动性
    gas_cost: 交易 Gas 成本（ETH）
    slippage: 滑点容忍度
    """
    # 使用 Uniswap V2 的恒定乘积做市模型
    # x * y = k
    reserve_in = pool_liquidity / 2
    reserve_out = pool_liquidity / 2

    # 步骤1：攻击者抢先买入（frontrun）
    frontrun_amount = victim_trade_size * 0.3  # 以受害者交易量的30%进行抢先
    amount_out_frontrun = (reserve_out * frontrun_amount) / (reserve_in + frontrun_amount)

    # 步骤2：受害者交易（资金池价格已被推高）
    new_reserve_in = reserve_in + frontrun_amount
    amount_out_victim = (reserve_out * victim_trade_size) / (new_reserve_in + victim_trade_size)

    # 步骤3：攻击者卖出（backrun）
    new_reserve_in2 = new_reserve_in + victim_trade_size
    sell_amount = amount_out_frontrun
    amount_back = (new_reserve_in2 * sell_amount) / (reserve_out + sell_amount)

    # 利润计算
    profit = amount_back - frontrun_amount - gas_cost
    victim_loss = victim_trade_size * slippage  # 简化的滑点损失

    return {
        'attacker_profit': profit,
        'victim_extra_slippage': victim_loss,
        'profitable': profit > 0,
        'attack_sequence': ['frontrun_buy', 'victim_trade', 'backrun_sell']
    }
