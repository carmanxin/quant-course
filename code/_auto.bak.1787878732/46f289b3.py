# @quantlab/output: 46f289b3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_orderbook(bids, asks, levels=10):
    """
    分析订单簿的微观结构特征

    bids: [(价格, 数量), ...] from highest to lowest
    asks: [(价格, 数量), ...] from lowest to highest
    """
    bid_prices = np.array([b[0] for b in bids[:levels]])
    bid_volumes = np.array([b[1] for b in bids[:levels]])
    ask_prices = np.array([a[0] for a in asks[:levels]])
    ask_volumes = np.array([a[1] for a in asks[:levels]])

    midpoint = (bid_prices[0] + ask_prices[0]) / 2
    spread = ask_prices[0] - bid_prices[0]
    spread_bps = spread / midpoint * 10000  # 以基点表示

    # 订单簿不平衡度
    total_bid_vol = np.sum(bid_volumes)
    total_ask_vol = np.sum(ask_volumes)
    imbalance = (total_bid_vol - total_ask_vol) / (total_bid_vol + total_ask_vol)

    # 斜率：衡量流动性的离散程度
    bid_slope = np.polyfit(range(levels), bid_volumes, 1)[0]
    ask_slope = np.polyfit(range(levels), ask_volumes, 1)[0]

    # 可视化
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 订单簿深度图
    x_bid = bid_prices
    y_bid = np.cumsum(bid_volumes)
    x_ask = ask_prices
    y_ask = np.cumsum(ask_volumes)

    axes[0].step(x_bid, y_bid, where='post', label='买盘', color='green', linewidth=2)
    axes[0].step(x_bid[-1], y_bid[-1])  # extend to meet ask
    axes[0].fill_between(x_bid, y_bid, step='post', alpha=0.3, color='green')

    axes[0].step(x_ask, y_ask, where='post', label='卖盘', color='red', linewidth=2)
    axes[0].fill_between(x_ask, y_ask, step='post', alpha=0.3, color='red')
    axes[0].axvline(x=midpoint, color='blue', linestyle='--', alpha=0.5, label=f'中间价={midpoint:.2f}')
    axes[0].set_xlabel('价格')
    axes[0].set_ylabel('累计挂单量')
    axes[0].set_title(f'订单簿深度 (价差={spread_bps:.1f} bps)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 成交量分布
    axes[1].barh(np.arange(levels), -bid_volumes[::-1], height=0.7, color='green', alpha=0.7, label='买盘')
    axes[1].barh(np.arange(levels), ask_volumes, height=0.7, color='red', alpha=0.7, label='卖盘')
    axes[1].axvline(x=0, color='black', linewidth=1)
    axes[1].set_yticks(np.arange(levels))
    axes[1].set_yticklabels([f'Level {i+1}' for i in range(levels)])
    axes[1].set_xlabel('挂单量')
    axes[1].set_title(f'各档位挂单量 (不平衡度={imbalance:.3f})')
    axes[1].legend()

    plt.tight_layout()
    plt.show()

    return {
        'spread': spread,
        'spread_bps': spread_bps,
        'imbalance': imbalance,
        'bid_slope': bid_slope,
        'ask_slope': ask_slope,
        'midpoint': midpoint
    }

# 模拟订单簿数据
# np.random.seed(42)
# mid = 100.0
# bid_prices = [mid - 0.01*(i+1) - np.random.rand()*0.005 for i in range(20)]
# ask_prices = [mid + 0.01*(i+1) + np.random.rand()*0.005 for i in range(20)]
# bid_volumes = [(p, int(np.random.exponential(500))) for p in bid_prices]
# ask_volumes = [(p, int(np.random.exponential(500))) for p in ask_prices]
# results = analyze_orderbook(bid_volumes, ask_volumes)
