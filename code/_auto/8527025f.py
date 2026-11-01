# @quantlab/output: 8527025f
import numpy as np
import pandas as pd

def dcf_valuation(free_cash_flows, growth_rate, terminal_growth, wacc,
                  projection_years=5, shares_outstanding=None):
    """
    两阶段DCF估值模型

    free_cash_flows: 历史自由现金流
    growth_rate: 预测期增长率
    terminal_growth: 永续增长率（通常2-3%）
    wacc: 加权平均资本成本
    projection_years: 预测期年数
    shares_outstanding: 总股本（如果提供则计算每股价值）
    """

    # 第一阶段：预测期现金流
    recent_fcf = free_cash_flows[-1]  # 最近一年的FCF

    projected_fcfs = []
    for t in range(1, projection_years + 1):
        fcf = recent_fcf * (1 + growth_rate) ** t
        projected_fcfs.append(fcf)

    # 第二阶段：终值（Gordon Growth Model）
    terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)

    # 折现回现值
    present_values = []
    for t, fcf in enumerate(projected_fcfs, 1):
        pv = fcf / (1 + wacc) ** t
        present_values.append(pv)

    pv_terminal = terminal_value / (1 + wacc) ** projection_years

    # 企业价值
    enterprise_value = sum(present_values) + pv_terminal

    # 每股价值
    per_share_value = enterprise_value / shares_outstanding if shares_outstanding else None

    # 各阶段价值占比
    stage1_pct = sum(present_values) / enterprise_value * 100
    stage2_pct = pv_terminal / enterprise_value * 100

    print("=== DCF估值结果 ===")
    print(f"预测期现金流现值: {sum(present_values):,.0f} ({stage1_pct:.1f}%)")
    print(f"终值现值: {pv_terminal:,.0f} ({stage2_pct:.1f}%)")
    print(f"企业价值: {enterprise_value:,.0f}")
    if per_share_value:
        print(f"每股价值: {per_share_value:.2f}")

    return {
        'enterprise_value': enterprise_value,
        'per_share_value': per_share_value,
        'projected_fcfs': projected_fcfs,
        'terminal_value': terminal_value,
        'stage1_pct': stage1_pct,
        'stage2_pct': stage2_pct
    }

# 使用示例
# fcf_history = [100, 108, 116, 125, 135]  # 过去5年自由现金流（百万）
# val = dcf_valuation(
#     free_cash_flows=fcf_history,
#     growth_rate=0.12,       # 预测期增长率12%
#     terminal_growth=0.03,   # 永续增长率3%
#     wacc=0.10,              # WACC 10%
#     projection_years=5,
#     shares_outstanding=50   # 5000万股
# )
