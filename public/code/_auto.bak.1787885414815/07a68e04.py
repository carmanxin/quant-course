# @quantlab/output: 07a68e04
import numpy as np
from collections import deque
from dataclasses import dataclass

@dataclass
class OrderBookSnapshot:
    """订单簿快照数据结构"""
    bid_prices: np.ndarray   # 买单价格（从高到低）
    bid_sizes: np.ndarray    # 买单数量
    ask_prices: np.ndarray   # 卖单价格（从低到高）
    ask_sizes: np.ndarray    # 卖单数量
    timestamp: float

class OrderBookAnalyzer:
    """订单簿分析器 - HFT信号生成"""

    def __init__(self, depth_levels=10):
        self.depth_levels = depth_levels
        self.snapshots = deque(maxlen=100)

    def calculate_weighted_imbalance(self, snapshot, decay=0.5):
        """计算加权订单簿不平衡度"""
        weights = np.array([decay**i for i in range(self.depth_levels)])

        # 截断到可用深度
        bid_sizes = snapshot.bid_sizes[:self.depth_levels]
        ask_sizes = snapshot.ask_sizes[:self.depth_levels]
        w = weights[:min(len(bid_sizes), len(ask_sizes))]

        weighted_bid = np.sum(w * bid_sizes[:len(w)])
        weighted_ask = np.sum(w * ask_sizes[:len(w)])
        total = weighted_bid + weighted_ask

        if total > 0:
            return (weighted_bid - weighted_ask) / total
        return 0.0

    def detect_large_orders(self, snapshot, size_threshold=500):
        """检测大单挂出"""
        large_bids = [(snapshot.bid_prices[i], snapshot.bid_sizes[i])
                     for i in range(min(len(snapshot.bid_prices), self.depth_levels))
                     if snapshot.bid_sizes[i] > size_threshold]
        large_asks = [(snapshot.ask_prices[i], snapshot.ask_sizes[i])
                     for i in range(min(len(snapshot.ask_prices), self.depth_levels))
                     if snapshot.ask_sizes[i] > size_threshold]
        return large_bids, large_asks

    def calculate_spread_dynamics(self, snapshot):
        """计算价差动态指标"""
        best_bid = snapshot.bid_prices[0]
        best_ask = snapshot.ask_prices[0]
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        spread_bp = spread / mid_price * 10000
        return mid_price, spread_bp

    def generate_signal(self, snapshot):
        """综合多个信号生成交易信号"""
        signals = {}

        # 1. 订单簿不平衡度
        imbalance = self.calculate_weighted_imbalance(snapshot)
        signals['imbalance'] = imbalance

        # 2. 大单检测
        large_bids, large_asks = self.detect_large_orders(snapshot)
        signals['large_bid_count'] = len(large_bids)
        signals['large_ask_count'] = len(large_asks)

        # 3. 价差
        mid_price, spread_bp = self.calculate_spread_dynamics(snapshot)
        signals['mid_price'] = mid_price
        signals['spread_bp'] = spread_bp

        # 4. 综合评分
        score = 0.0
        score += imbalance * 0.4                          # 不平衡权重40%
        score += (len(large_asks) - len(large_bids)) * 0.1  # 大单信号20%
        if spread_bp < 1.0:  # 价差极窄，流动性好
            score += 0.1
        elif spread_bp > 5.0:  # 价差宽，流动性差
            score -= 0.2

        signals['composite_score'] = score
        return signals

# ===== 模拟订单簿数据流 =====
np.random.seed(123)
analyzer = OrderBookAnalyzer(depth_levels=10)

# 模拟若干订单簿快照
for i in range(20):
    mid = 100.0
    # 生成买卖订单簿
    bid_prices = np.array([mid - 0.01 * (j+1) + np.random.normal(0, 0.002) for j in range(10)])
    ask_prices = np.array([mid + 0.01 * (j+1) + np.random.normal(0, 0.002) for j in range(10)])
    bid_sizes = np.random.gamma(shape=2, scale=100, size=10).astype(int)
    ask_sizes = np.random.gamma(shape=2, scale=100, size=10).astype(int)

    # 在某些时间点注入大单
    if i % 5 == 0:
        bid_sizes[1] = 1000  # 一个大买单
    if i % 7 == 0:
        ask_sizes[0] = 800   # 一个大卖单

    snapshot = OrderBookSnapshot(bid_prices, bid_sizes, ask_prices, ask_sizes, i)
    signals = analyzer.generate_signal(snapshot)

    action = "HOLD"
    if signals['composite_score'] > 0.25:
        action = "BUY"
    elif signals['composite_score'] < -0.25:
        action = "SELL"

    print(f"Snapshot {i:2d}: score={signals['composite_score']:+.3f} "
          f"| imbalance={signals['imbalance']:+.3f} "
          f"| spread={signals['spread_bp']:.1f}bp "
          f"| action={action}")
