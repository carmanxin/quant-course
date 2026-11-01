# @quantlab/output: 21bda122
bids = [(100,100),(99.5,200),(99,300)]  # (价格,数量)
total_shares = 500
cost = 0
for price, volume in bids:
    if total_shares <= 0: break
    executed = min(total_shares, volume)
    cost += executed * price
    total_shares -= executed
avg_price = cost / 500
impact = (avg_price - bids[0][0]) / bids[0][0]
print(f"冲击成本: {impact:.2%}")
