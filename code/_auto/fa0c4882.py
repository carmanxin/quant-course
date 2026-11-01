# @quantlab/output: fa0c4882
def impermanent_loss(P_ratio):
    """
    计算无常损失
    P_ratio: 价格变动倍数 P_new / P_initial
    返回：无常损失百分比
    """
    return 1 - (2 * np.sqrt(P_ratio)) / (1 + P_ratio)

def il_with_fees(P_ratio, fee_apr, holding_period_years):
    """
    考虑手续费收入后的净无常损失
    """
    il = impermanent_loss(P_ratio)
    fee_income = fee_apr * holding_period_years
    net_return = fee_income - il  # 正值为赚钱
    return {
        'impermanent_loss': il,
        'fee_income': fee_income,
        'net_return': net_return
    }

# 无常损失对照表
print("无常损失随价格变化的对照表:")
print(f"{'价格倍数':<12} {'无常损失':<12}")
for ratio in [0.5, 0.75, 0.9, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0]:
    il = impermanent_loss(ratio)
    print(f"{ratio:<12.2f} {il*100:<12.4f}%")

# 示例：价格涨1倍，IL约5.7%
print(f"\n价格翻倍时的IL: {impermanent_loss(2.0)*100:.2f}%")
