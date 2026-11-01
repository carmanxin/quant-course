# @quantlab/output: 4360dae0
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List

@dataclass
class Execution:
    """单笔执行记录"""
    timestamp: pd.Timestamp
    quantity: int
    price: float
    side: str  # 'BUY' or 'SELL'

class TransactionCostAnalyzer:
    """交易成本分析器 (TCA)"""

    def __init__(self, arrival_price, decision_time, side, total_target_qty):
        self.arrival_price = arrival_price
        self.decision_time = decision_time
        self.side = side
        self.total_target_qty = total_target_qty
        self.executions: List[Execution] = []
        self.commission_rate = 0.0002  # 2bp
        self.fee_rate = 0.0001          # 1bp

    def add_execution(self, exec_: Execution):
        self.executions.append(exec_)

    def calculate_implementation_shortfall(self, close_price=None):
        """
        计算执行缺口及其成分分解

        返回字典，包含各成分的bp值
        """
        if not self.executions:
            return None

        total_qty = sum(e.quantity for e in self.executions)
        avg_exec_price = sum(e.quantity * e.price for e in self.executions) / total_qty

        # 1. 佣金
        total_value = sum(e.quantity * e.price for e in self.executions)
        commission = total_value * self.commission_rate
        commission_bp = commission / (total_qty * self.arrival_price) * 10000

        # 2. 交易所费用
        fee = total_value * self.fee_rate
        fee_bp = fee / (total_qty * self.arrival_price) * 10000

        # 3. 执行缺口（以到达价为基准）
        if self.side == 'BUY':
            is_raw = (avg_exec_price - self.arrival_price) / self.arrival_price * 10000
        else:
            is_raw = (self.arrival_price - avg_exec_price) / self.arrival_price * 10000

        # 4. 机会成本（未成交部分）
        unfilled = self.total_target_qty - total_qty
        opportunity_cost_bp = 0
        if unfilled > 0 and close_price is not None:
            if self.side == 'BUY':
                opp_cost = unfilled * (close_price - self.arrival_price)
            else:
                opp_cost = unfilled * (self.arrival_price - close_price)
            opportunity_cost_bp = opp_cost / (self.total_target_qty * self.arrival_price) * 10000

        # 5. 总成本汇总
        total_cost_bp = is_raw + commission_bp + fee_bp + opportunity_cost_bp

        return {
            'arrival_price': self.arrival_price,
            'avg_exec_price': avg_exec_price,
            'total_exec_qty': total_qty,
            'unfilled_qty': unfilled,
            'completion_rate': total_qty / self.total_target_qty * 100,
            'is_bp': is_raw,
            'commission_bp': commission_bp,
            'fee_bp': fee_bp,
            'opportunity_cost_bp': opportunity_cost_bp,
            'total_cost_bp': total_cost_bp,
        }

    def calculate_market_impact(self, adv, sigma_daily):
        """
        使用平方根模型估计市场冲击

        adv: 日均成交量
        sigma_daily: 日波动率
        """
        total_qty = sum(e.quantity for e in self.executions)
        participation_rate = total_qty / adv

        # 平方根模型
        Y = 0.5  # 缩放因子
        impact_pct = sigma_daily * np.sqrt(participation_rate) * Y
        impact_bp = impact_pct * 10000

        return {
            'participation_rate': participation_rate,
            'estimated_impact_bp': impact_bp,
            'adv': adv,
            'sigma_daily': sigma_daily
        }

    def benchmark_comparison(self, market_vwap, market_open, market_close):
        """
        多基准对比分析
        """
        total_qty = sum(e.quantity for e in self.executions)
        avg_exec_price = sum(e.quantity * e.price for e in self.executions) / total_qty

        vs_arrival = (avg_exec_price - self.arrival_price) / self.arrival_price * 10000
        vs_vwap = (avg_exec_price - market_vwap) / market_vwap * 10000
        vs_close = (avg_exec_price - market_close) / market_close * 10000

        return {
            'vs_arrival_bp': vs_arrival,
            'vs_vwap_bp': vs_vwap,
            'vs_close_bp': vs_close,
        }

# ===== TCA使用示例 =====
analyzer = TransactionCostAnalyzer(
    arrival_price=100.0,
    decision_time=pd.Timestamp('2024-01-15 09:30:00'),
    side='BUY',
    total_target_qty=10000
)

# 模拟分批成交记录
np.random.seed(42)
exec_prices = [100.05, 100.08, 100.12, 100.15, 100.10,
               100.20, 100.18, 100.22, 100.25, 100.30]
exec_qtys = [1000] * 10

for i, (price, qty) in enumerate(zip(exec_prices, exec_qtys)):
    analyzer.add_execution(Execution(
        timestamp=pd.Timestamp(f'2024-01-15 09:3{i}:00'),
        quantity=qty, price=price, side='BUY'
    ))

# 计算执行缺口
is_result = analyzer.calculate_implementation_shortfall(close_price=100.50)
print("=" * 55)
print("执行缺口分析 (Implementation Shortfall)")
print("=" * 55)
print(f"到达价:     {is_result['arrival_price']:.2f}")
print(f"实际均价:   {is_result['avg_exec_price']:.4f}")
print(f"成交量:     {is_result['total_exec_qty']} / {10000}")
print(f"完成率:     {is_result['completion_rate']:.1f}%")
print("-" * 55)
print(f"价格滑点:   {is_result['is_bp']:>8.2f} bp")
print(f"佣金成本:   {is_result['commission_bp']:>8.2f} bp")
print(f"交易所费:   {is_result['fee_bp']:>8.2f} bp")
print(f"机会成本:   {is_result['opportunity_cost_bp']:>8.2f} bp")
print(f"──────────────────────────")
print(f"总成本:     {is_result['total_cost_bp']:>8.2f} bp")
print(f"总成本(美元): {(is_result['total_cost_bp']/10000 * 10000 * 100):.2f}")

# 市场冲击估计
impact = analyzer.calculate_market_impact(adv=500000, sigma_daily=0.02)
print(f"\n市场冲击估计（平方根模型）:")
print(f"  参与率: {impact['participation_rate']:.4%}")
print(f"  估计冲击: {impact['estimated_impact_bp']:.2f} bp")

# 多基准对比
benchmarks = analyzer.benchmark_comparison(
    market_vwap=100.15, market_open=100.0, market_close=100.50
)
print(f"\n多基准对比:")
print(f"  vs 到达价: {benchmarks['vs_arrival_bp']:.2f} bp")
print(f"  vs VWAP:   {benchmarks['vs_vwap_bp']:.2f} bp")
print(f"  vs 收盘价: {benchmarks['vs_close_bp']:.2f} bp")
