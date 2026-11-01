# @quantlab/output: 2.1-microstructure
bids = [(100, 100), (99.5, 200), (99, 300)]
total_shares = 500
cost = 0
remaining = total_shares
for price, volume in bids:
    if remaining <= 0:
        break
    executed = min(remaining, volume)
    cost += executed * price
    remaining -= executed
avg_price = cost / total_shares
impact = (avg_price - bids[0][0]) / bids[0][0]
print(f'平均成交价: {avg_price:.2f}')
print(f'冲击成本: {impact:.4%}')
