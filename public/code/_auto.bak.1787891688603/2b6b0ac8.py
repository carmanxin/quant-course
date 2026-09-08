# @quantlab/output: 2b6b0ac8
# 计算"一张期权"的实际名义金额
opt_unit_price = 0.0465  # 一份 ATM 期权价格
contract_multiplier = 10000
notional_per_lot = opt_unit_price * contract_multiplier
print(f"1 张 ATM 50ETF 期权名义金额: {notional_per_lot:,.2f} 元")
print(f"对应标的价值:   2.800 × 10000 = {2.800 * 10000:,.2f} 元")
print(f"期权 / 标的比:  {opt_unit_price/2.800*100:.2f}%")
