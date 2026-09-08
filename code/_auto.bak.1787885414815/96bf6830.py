# @quantlab/output: 96bf6830
# 涨跌停模拟: 50ETF 涨停时,Call 期权价格行为
S_now = 2.800
S_up_limit = 2.800 * 1.10  # 2.800 + 10%
K_call = 2.940
T = 30/365
# ATM Call 在 S=2.800 的合理价格
bs_value = bs(S_now, K_call, T, 0.025, 0.18, "call")
# 当 S = 涨停价 3.080 时
bs_at_limit = bs(S_up_limit, K_call, T, 0.025, 0.18, "call")
print(f"50ETF 涨停 3.080 时,行权 2.940 Call 的内在价值: {(S_up_limit-K_call)*10000:.0f} 元/张")
print(f"BS 理论价格: {bs_at_limit*10000:.0f} 元/张")
print(f"差距: {(bs_at_limit - (S_up_limit-K_call))*10000:.0f} 元/张 (时间价值剩余)")
print(f"风险: 涨停封单导致无法卖出平仓,只能等待标的回落")
