# @quantlab/output: 903a68f8
import numpy as np

# 假设未来 60 天, 沪深 300 价格 3800 → 不同情景
scenarios = [3500, 3600, 3700, 3800, 3900, 4000, 4100]
ho_put_intrinsic = lambda ST, K=3800: max(K-ST, 0)
put_cost = 120 * contract_multiplier  # 12,000 元/张
contracts_held = 7.4  # 约 7-8 张

# 假设 50ETF 价格变动对应沪深 300 (即 beta=1)
# 50ETF 简单线性外推: 1% HS300 变动 ≈ 1% 50ETF 变动
S = 2.800
etf_holdings = 1_000_000

print(f"{'HS300':>6} {'50ETF':>6} {'ETF损益':>10} {'Put损益':>10} {'净额':>10} {'对冲效果'}")
for ST_hs300 in scenarios:
    # ETF 跟随 HS300 变动 (简化)
    pct_change = (ST_hs300 - hs300) / hs300
    S_etf = S * (1 + pct_change)
    etf_pnl = (S_etf - S) * etf_holdings

    # Put 损益:到期内在价值 - 权利金
    intrinsic = max(3800 - ST_hs300, 0)
    put_pnl = (intrinsic * contract_multiplier - put_cost) * contracts_held

    net = etf_pnl + put_pnl
    label = "完美对冲" if abs(net) < etf_pnl*0.2 else "部分对冲"
    print(f"{ST_hs300:>6.0f} {S_etf:>6.3f} {etf_pnl:>10.0f} {put_pnl:>10.0f} {net:>10.0f}  {label}")
