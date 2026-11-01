# @quantlab/output: a7e1a7d3
# 假设组合 beta ≈ 1.0(相对沪深 300)
# 50ETF 持仓市值 = 2.800 × 1000000 = 280 万
# 沪深 300 现价 ≈ 3800
# 需要对冲的市场风险 = 280 万元 × 1.0 (beta) / 3800 × 100 = 7.37 张 HO Put

portfolio_value = 2.800 * 1_000_000  # 280万
beta = 1.0
hs300 = 3800
contract_multiplier = 100  # 100元/点
# 需要的合约数 = portfolio_value × beta / (hs300 × contract_multiplier)
contracts = portfolio_value * beta / (hs300 * contract_multiplier)
print(f"按 beta=1 对冲: {contracts:.1f} 张 HO Put P3800")
print(f"实际对冲成本: {contracts * 12_000:,.0f} 元")
print(f"占组合比例:   {contracts*12_000/portfolio_value*100:.2f}%")
