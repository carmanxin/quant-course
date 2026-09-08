# @quantlab/output: ca098ca8
import numpy as np
import pandas as pd

# 模拟订单簿深度
np.random.seed(42)
bid_levels = np.array([100.0, 99.9, 99.8, 99.7, 99.6, 99.5, 99.4, 99.3, 99.2, 99.1])
ask_levels = np.array([100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0])
volumes = np.array([50, 100, 150, 200, 300, 400, 500, 600, 800, 1000])  # 每个价位的挂单量

def execute_market_buy(quantity, ask_levels, volumes):
    """模拟市价买单在订单簿中的成交过程"""
    remaining = quantity
    total_cost = 0.0
    filled = 0

    for price, vol in zip(ask_levels, volumes):
        if remaining <= 0:
            break
        fill_qty = min(remaining, vol)
        total_cost += fill_qty * price
        filled += fill_qty
        remaining -= fill_qty

    avg_price = total_cost / filled if filled > 0 else None
    return avg_price, filled, remaining

# 不同订单量下的冲击
mid_price = (bid_levels[0] + ask_levels[0]) / 2
for order_qty in [50, 200, 500, 1500, 3000]:
    avg_price, filled, unfilled = execute_market_buy(order_qty, ask_levels, volumes)
    if avg_price:
        slippage = (avg_price - mid_price) / mid_price * 10000  # bp
        print(f"订单量: {order_qty:5d}  均价: {avg_price:.2f}  滑点: {slippage:.2f}bp  未成交: {unfilled}")
