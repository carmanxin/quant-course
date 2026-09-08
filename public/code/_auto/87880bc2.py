# @quantlab/output: 87880bc2
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class Venue(Enum):
    LIT_EXCHANGE = "LIT"
    DARK_POOL_A = "DARK_A"
    DARK_POOL_B = "DARK_B"
    INTERNALIZER = "INT"

@dataclass
class VenueCharacteristics:
    """交易场所特征"""
    venue: Venue
    avg_fill_rate: float          # 平均成交率
    avg_fill_time_seconds: float  # 平均成交时间
    price_improvement_bp: float   # 相比NBBO的价格改善（bp）
    min_order_qty: int = 0       # 最小订单量
    fee_per_share: float = 0.0   # 费用（每100股）
    is_anonymous: bool = True    # 是否匿名

class SmartOrderRouter:
    """智能订单路由器 (SOR)"""

    def __init__(self):
        self.venues = self._initialize_venues()
        self.preference_weights = {
            'fill_probability': 0.35,
            'price_improvement': 0.30,
            'speed': 0.20,
            'anonymity': 0.10,
            'fee': 0.05,
        }

    def _initialize_venues(self) -> List[VenueCharacteristics]:
        """初始化可用的交易场所"""
        return [
            VenueCharacteristics(
                Venue.LIT_EXCHANGE,
                avg_fill_rate=0.99,
                avg_fill_time_seconds=0.001,
                price_improvement_bp=0,
                is_anonymous=False,
                fee_per_share=0.003,
            ),
            VenueCharacteristics(
                Venue.DARK_POOL_A,
                avg_fill_rate=0.60,
                avg_fill_time_seconds=5.0,
                price_improvement_bp=2.5,  # 半价差改善
                min_order_qty=500,
                fee_per_share=0.001,
            ),
            VenueCharacteristics(
                Venue.DARK_POOL_B,
                avg_fill_rate=0.45,
                avg_fill_time_seconds=2.0,
                price_improvement_bp=3.0,
                min_order_qty=1000,
                fee_per_share=0.002,
            ),
            VenueCharacteristics(
                Venue.INTERNALIZER,
                avg_fill_rate=0.70,
                avg_fill_time_seconds=0.5,
                price_improvement_bp=1.0,
                min_order_qty=200,
                fee_per_share=0.0,  # 内部化器通常免佣金
            ),
        ]

    def route_order(self, order_qty: int, spread_bp: float,
                    urgency: str = 'normal',
                    market_depth: int = 10000) -> Dict[Venue, int]:
        """
        为订单选择最优的交易场所分配

        参数:
            order_qty: 订单数量
            spread_bp: 当前买卖价差(bp)
            urgency: 'urgent'(立即成交优先) / 'normal' / 'patient'(成本优化优先)
            market_depth: 公开市场深度(NBBO档位挂单量)
        """
        eligible_venues = []

        for venue in self.venues:
            # 最小订单量检查
            if venue.min_order_qty > 0 and order_qty < venue.min_order_qty:
                continue

            # 评分各场所
            scores = {}

            # 1. 成交概率得分
            fill_score = venue.avg_fill_rate

            # 2. 价格改善（与价差的比率）
            if spread_bp > 0:
                price_score = venue.price_improvement_bp / spread_bp
            else:
                price_score = 0

            # 3. 速度得分（越快越好，归一化到[0,1]）
            max_time = max(v.avg_fill_time_seconds for v in self.venues)
            speed_score = 1 - venue.avg_fill_time_seconds / (max_time + 1)

            # 4. 匿名性得分
            anonymity_score = 1.0 if venue.is_anonymous else 0.3

            # 5. 费用得分（越低越好）
            max_fee = max(v.fee_per_share for v in self.venues)
            fee_score = 1 - venue.fee_per_share / (max_fee + 0.0001)

            # 综合加权得分
            if urgency == 'urgent':
                weights = {'fill_probability': 0.60, 'speed': 0.25,
                          'price_improvement': 0.10, 'fee': 0.03, 'anonymity': 0.02}
            elif urgency == 'patient':
                weights = {'fill_probability': 0.15, 'speed': 0.05,
                          'price_improvement': 0.45, 'fee': 0.20, 'anonymity': 0.15}
            else:  # normal
                weights = self.preference_weights

            composite = (
                weights['fill_probability'] * fill_score +
                weights['price_improvement'] * price_score +
                weights['speed'] * speed_score +
                weights['anonymity'] * anonymity_score +
                weights['fee'] * fee_score
            )

            eligible_venues.append((venue, composite, fill_score, price_score))

        # 按综合得分排序
        eligible_venues.sort(key=lambda x: x[1], reverse=True)

        # 分配订单
        allocation = {}
        remaining_qty = order_qty

        # 小订单直接发到最优场所
        if order_qty <= market_depth:
            best_venue = eligible_venues[0][0]
            allocation[best_venue.venue] = order_qty
            return allocation

        # 大订单分拆到多个场所
        # 策略: 60%公开市场保证成交, 40%暗池寻求价格改善
        lit_qty = int(order_qty * 0.6)
        dark_qty = order_qty - lit_qty

        # 找到公开市场
        lit_venues = [v for v, _, _, _ in eligible_venues
                     if v.venue == Venue.LIT_EXCHANGE]
        if lit_venues:
            allocation[Venue.LIT_EXCHANGE] = lit_qty

        # 剩余分配到暗池（按得分比例）
        dark_venues = [(v, score) for v, score, _, _ in eligible_venues
                      if v.venue != Venue.LIT_EXCHANGE]
        if dark_venues and dark_qty > 0:
            total_score = sum(s for _, s in dark_venues)
            for venue, score in dark_venues:
                venue_qty = int(dark_qty * score / total_score)
                if venue_qty >= venue.min_order_qty:
                    allocation[venue.venue] = venue_qty

        return allocation

    def analyze_routing_decision(self, order_qty, spread_bp, market_depth):
        """生成路由决策的分析报告"""
        print(f"\n订单路由分析:")
        print(f"  订单量: {order_qty:,} 股")
        print(f"  价差: {spread_bp:.1f} bp")
        print(f"  公开深度: {market_depth:,} 股")

        for urgency in ['urgent', 'normal', 'patient']:
            alloc = self.route_order(order_qty, spread_bp, urgency, market_depth)
            total_pct = sum(alloc.values()) / order_qty * 100
            print(f"\n  紧急度: {urgency} (分配率={total_pct:.0f}%)")
            for venue, qty in alloc.items():
                pct = qty / order_qty * 100
                print(f"    {venue.value:>10}: {qty:>8,} 股 ({pct:>5.1f}%)")

# ===== SOR使用示例 =====
sor = SmartOrderRouter()

# 场景1：中等订单，中等价差
sor.analyze_routing_decision(order_qty=5000, spread_bp=5.0, market_depth=10000)

# 场景2：大订单，宽价差
sor.analyze_routing_decision(order_qty=50000, spread_bp=15.0, market_depth=5000)

# 场景3：小订单，窄价差
sor.analyze_routing_decision(order_qty=200, spread_bp=2.0, market_depth=100000)
