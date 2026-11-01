# @quantlab/output: 7bf097f3
# 长期 Call OTM 5% 的对冲设计
S = 2.744       # 大宗交易价格
K_long = 2.880  # OTM 5%
T = 180/365
r = 0.025
sigma = 0.18  # 6 个月远期波动率假设

call_long = bs_call(S, K_long, T, r, sigma)
print(f"长期 Call 权利金: {call_long:.4f} 元/份 = {call_long*10000:.0f} 元/张")

# 计算对冲总成本
n_contracts = 100  # 100 张 = 100 万份
total_cost = call_long * 10000 * n_contracts
print(f"100 张总成本: {total_cost:,.0f} 元")
print(f"相当于大宗交易总值的 {total_cost/(2.744*1_000_000)*100:.2f}%")

# 关键参数
print(f"行权价 K={K_long}, 盈亏平衡点: S + 期权成本 = {K_long + call_long:.3f}")
