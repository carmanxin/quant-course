# @quantlab/output: cceb6b92
# 仓位 1: Long ATM Put T1=30d, Vega = 0.20
# 加仓: Long OTM Put T2=90d, Vega = 0.30
# 设置 Vega 中性 → 找 Vega 中性的对冲比例

vega_atm_30d = 0.20
vega_otm_90d = 0.30
ratio = -vega_atm_30d / vega_otm_90d  # 持仓 + 对冲 = 0
print(f"Vega 中性所需对冲: Short {abs(ratio):.2f} 张 OTM Put T2")
# 检查 Gamma(此时 Gamma 不一定中性)
gamma_atm_30d = 0.018
gamma_otm_90d = 0.013
combined_gamma = 1 * gamma_atm_30d + ratio * gamma_otm_90d
print(f"此时组合 Gamma = {combined_gamma:.4f} (不为零)")
print(f"→ Vega 中性但 Gamma 正, 适合温和看多波动")
