# @quantlab/output: f0aebb48
import numpy as np
import pandas as pd

class CostSimulator:
    """
    交易成本模拟器：从回测信号到扣除成本后的净值
    """

    def __init__(self, commission_rate=0.0003, stamp_tax_rate=0.0005,
                 slippage_bps=1.0, impact_model='linear'):
        """
        commission_rate: 佣金费率（万3）
        stamp_tax_rate: 印花税率（万5，仅在卖出时收取）
        slippage_bps: 滑点（基点）
        impact_model: 冲击模型 ('linear', 'sqrt')
        """
        self.commission_rate = commission_rate
        self.stamp_tax_rate = stamp_tax_rate
        self.slippage_bps = slippage_bps / 10000  # 转换为百分比
        self.impact_model = impact_model

    def compute_costs(self, positions, prices, volumes=None):
        """
        positions: 每日目标仓位（0-1，表示持仓比例）
        prices: 每日价格
        volumes: 每日市场成交量（可选，用于冲击模型）

        返回扣费后的净值序列
        """
        n = len(positions)
        trades = np.diff(positions, prepend=0)  # 每日仓位变化
        turnover = np.abs(trades)  # 每日换手率

        # 计算各类成本
        commission_cost = turnover * self.commission_rate  # 买卖双向佣金

        # 印花税仅在卖出时（trades < 0 表示减仓）
        stamp_cost = np.where(trades < 0, -trades * self.stamp_tax_rate, 0)

        # 滑点
        slippage_cost = turnover * self.slippage_bps

        total_cost_rate = commission_cost + stamp_cost + slippage_cost

        # 价格收益率
        price_returns = np.diff(np.log(prices), prepend=np.log(prices[0]))
        price_returns[0] = 0

        # 策略总收益 = 持仓收益 - 交易成本
        strategy_returns = positions * price_returns - total_cost_rate

        # 累计净值
        nav = np.cumprod(1 + strategy_returns)

        return nav, {
            'total_commission': np.sum(commission_cost),
            'total_stamp': np.sum(stamp_cost),
            'total_slippage': np.sum(slippage_cost),
            'total_turnover': np.sum(turnover),
            'avg_cost_per_trade': np.mean(total_cost_rate[turnover > 0]) if np.any(turnover > 0) else 0
        }

# 一键运行(用 signal 当仓位, df['Close'] 当价格)
# 注: cost simulator 期望 positions in [0, 1] 表示持仓比例,
# 而教学片段里的 signal 是 [-1, 0, 1], 所以映射到 [-1, 1] 再 + 1 / 2 → [0, 1]
positions_q = (signal + 1) / 2.0
prices_q = df['Close'].values

simulator = CostSimulator(commission_rate=0.00025, slippage_bps=2.0)
nav_costed, cost_report = simulator.compute_costs(positions_q, prices_q)
total_cost = (
    cost_report['total_commission']
    + cost_report['total_stamp']
    + cost_report['total_slippage']
)
print('=' * 50)
print(f"✅ 总换手率:     {cost_report['total_turnover']:.2%}")
print(f"✅ 总交易成本:   {total_cost:.4%}")
print(f"✅ 佣金:         {cost_report['total_commission']:.4%}")
print(f"✅ 印花税:       {cost_report['total_stamp']:.4%}")
print(f"✅ 滑点:         {cost_report['total_slippage']:.4%}")
print(f"✅ 扣除成本终值: ${nav_costed[-1]:,.0f}  (vs 无成本初始 {len(nav_costed)*10000:,.0f})")
