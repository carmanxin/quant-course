# @quantlab/output: 095a9ebc
# Bull Call Spread 收益
K1, K2 = 2.800, 2.950
c1 = bs(S, K1, T, r, sigma, "call")
c2 = bs(S, K2, T, r, sigma, "call")
net_cost = (c1 - c2) * 10000  # 净权利金支出
print(f"Bull Call Spread 净成本: {net_cost:.0f} 元/对(2张)")
print(f"最大盈利: {(K2-K1)*10000 - net_cost:.0f} 元(到期 S >= {K2})")
print(f"最大亏损: {net_cost:.0f} 元(到期 S <= {K1})")
print(f"盈亏平衡: S = {K1 + net_cost/10000:.4f}")
