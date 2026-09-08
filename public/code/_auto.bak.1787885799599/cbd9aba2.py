# @quantlab/output: cbd9aba2
# Protective Put 收益分析
K_put = 2.660  # OTM 5%
put_premium = bs(S, K_put, T, r, sigma, "put")  # 假设 IV 0.22
print(f"买入 OTM 5% Put 权利金: {put_premium*10000:.0f} 元/张")

# 关键节点
print(f"\n{'到期价':>8} {'ETF损益':>10} {'Put损益':>10} {'净损益':>10}")
for ST in [2.50, 2.60, 2.66, 2.70, 2.80, 2.90, 3.00]:
    etf_pnl = (ST-S)*10000
    put_pnl = (max(K_put-ST, 0)*10000 - put_premium*10000)
    net = etf_pnl + put_pnl
    label = ""
    if ST <= K_put:
        label = "(受到保护)"
    print(f"{ST:>8.3f} {etf_pnl:>+10.0f} {put_pnl:>+10.0f} {net:>+10.0f}  {label}")
