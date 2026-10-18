# @quantlab/output: 4fa960fc
import numpy as np

def compare_order_costs(mid_price, spread_bp, order_type, quantity,
                        fill_prob=0.8, impact_coeff=0.0001):
    """
    系统对比不同订单类型的预期成本

    spread_bp: 当前买卖价差（bp）
    order_type: "market" / "limit" / "iceberg"
    quantity: 订单数量
    fill_prob: 限价单的预期成交概率
    impact_coeff: 市场冲击系数
    """
    half_spread = spread_bp / 2 / 10000.0 * mid_price

    results = {}

    # 市价单成本: 半价差 + 市场冲击
    market_impact = impact_coeff * np.sqrt(quantity / 1000) * mid_price
    market_cost = half_spread + market_impact

    # 限价单成本: 预期冲击（部分成交时）+ 机会成本
    limit_impact = impact_coeff * np.sqrt(quantity * fill_prob / 1000) * mid_price
    opportunity_cost = (1 - fill_prob) * spread_bp / 10000.0 * mid_price
    limit_cost = half_spread * fill_prob + limit_impact * fill_prob + opportunity_cost

    # 冰山订单成本: 介于市价单和限价单之间
    iceberg_visibility = 0.1  # 只显示10%
    iceberg_impact = impact_coeff * np.sqrt(quantity * iceberg_visibility / 1000) * mid_price
    iceberg_cost = half_spread + iceberg_impact * 0.7

    return {
        "市价单": {"成本(bp)": market_cost / mid_price * 10000, "确定性": "高"},
        "限价单": {"成本(bp)": limit_cost / mid_price * 10000, "确定性": f"成交概率{fill_prob:.0%}"},
        "冰山订单": {"成本(bp)": iceberg_cost / mid_price * 10000, "确定性": "中高"},
    }

# 测试
mid_price = 100.0
for qty in [100, 1000, 10000]:
    print(f"\n数量 = {qty} 股（中间价 = {mid_price}，买卖价差 = 5bp）:")
    costs = compare_order_costs(mid_price, 5, None, qty)
    for order_type, info in costs.items():
        print(f"  {order_type}: 预期成本 {info['成本(bp)']:.2f}bp, {info['确定性']}")
