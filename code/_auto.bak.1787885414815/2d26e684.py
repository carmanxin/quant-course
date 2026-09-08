# @quantlab/output: 2d26e684
cost_rate = 0.001
trades = df['position'].diff().abs()
cost = trades * df['Close'] * cost_rate
net_returns = strategy_returns - cost / capital
