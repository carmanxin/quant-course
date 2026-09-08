# @quantlab/output: 300106fc
def gamma_scalping_pnl(gamma_per_day, sigma_daily, theta_per_day, n_days, transaction_cost=0.0):
    """伽马剥头皮收益近似"""
    expected_dS2 = sigma_daily ** 2  # 单日波动率的平方
    gross_pnl_per_day = 0.5 * gamma_per_day * expected_dS2
    net_pnl = (gross_pnl_per_day - theta_per_day) * n_days - transaction_cost
    return net_pnl

# 示例: Long Straddle 的 Gamma + Theta
# Straddle 在 ATM 的 Gamma ≈ 0.02 (per S^2)
# Theta ≈ -0.05 / day
# sigma_daily = 0.014
print(f"每日 Gamma 收益: {0.5 * 0.02 * 0.014**2:.6f}")
print(f"每日 Theta 损失: {-0.05:.4f}")
print(f"结论: Gamma 收益远小于 Theta 损失,必须等大幅波动")
