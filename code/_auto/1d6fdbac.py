# @quantlab/output: 1d6fdbac
strategies = {
    "Long Call (单边看涨)": [(+1, "call", 100)],
    "Long Straddle (ATM)":  [(+1, "call", 100), (+1, "put", 100)],
    "Long Strangle (OTM)": [(+1, "call", 105), (+1, "put", 95)],
    "Short Strangle (卖方)":[(-1, "call", 105), (-1, "put", 95)],
    "Long Butterfly":       [(+1, "call", 95), (-2, "call", 100), (+1, "call", 105)],
    "Iron Condor (卖方)": [(-1, "put", 95), (+1, "put", 90),
                            (-1, "call", 105), (+1, "call", 110)],
    "Bull Call Spread":     [(+1, "call", 100), (-1, "call", 105)],
    "Bear Put Spread":      [(+1, "put", 100), (-1, "put", 95)],
}

def payoff_at_expiry(legs, S_T, S_0, T, r, sigma):
    """计算到期时组合价值变化"""
    portfolio_value = 0
    initial_cost = 0
    for qty, otype, K in legs:
        cost = bs(S_0, K, T, r, sigma, otype) * abs(qty) * 10000
        initial_cost += cost if qty > 0 else -cost

        if otype == "call":
            payoff = max(S_T - K, 0) * 10000
        else:
            payoff = max(K - S_T, 0) * 10000
        portfolio_value += qty * payoff
    return portfolio_value - initial_cost

# 计算盈亏平衡点
S_range = np.linspace(70, 130, 600)
for name, legs in strategies.items():
    payoffs = np.array([payoff_at_expiry(legs, s, 100, 30/365, 0.03, 0.20) for s in S_range])

    # 找盈亏平衡点
    breakevens = []
    for i in range(len(S_range)-1):
        if payoffs[i] * payoffs[i+1] < 0:
            breakevens.append((S_range[i] + S_range[i+1]) / 2)

    print(f"{name}:")
    print(f"  最大收益: {payoffs.max():.0f} 元 | 最大亏损: {payoffs.min():.0f} 元")
    print(f"  盈亏平衡点: {[round(b,2) for b in breakevens]}")
