# @quantlab/output: 87071047
import numpy as np
import pandas as pd

class AlgoExecutor:
    """算法执行引擎 - 实现TWAP、VWAP、POV三种基本算法"""

    def __init__(self, total_quantity, side='BUY'):
        self.total_qty = total_quantity
        self.remaining = total_quantity
        self.side = side  # BUY or SELL
        self.executed = []

    def twap_schedule(self, n_slices):
        """TWAP：均匀拆分"""
        base_qty = self.total_qty // n_slices
        schedule = [base_qty] * n_slices
        # 将余数分配给前面的时间片
        remainder = self.total_qty - sum(schedule)
        for i in range(remainder):
            schedule[i] += 1
        return schedule

    def vwap_schedule(self, volume_profile, n_slices):
        """VWAP：根据历史成交量分布拆分"""
        if isinstance(volume_profile, list):
            volume_profile = np.array(volume_profile)
        total_vol = volume_profile.sum()
        fractions = volume_profile / total_vol
        schedule = (fractions * self.total_qty).astype(int)
        return schedule

    def pov_execute(self, market_volume, participation_rate):
        """POV：以固定比例参与市场"""
        target_qty = int(market_volume * participation_rate)
        actual_qty = min(target_qty, self.remaining)
        self.remaining -= actual_qty
        self.executed.append({
            'quantity': actual_qty,
            'participation_rate': participation_rate,
            'remaining': self.remaining
        })
        return actual_qty

    def calculate_execution_metrics(self, executed_prices, benchmark_price):
        """计算执行质量指标"""
        executed_prices = np.array(executed_prices)
        avg_exec_price = executed_prices.mean()

        # VWAP滑点
        vwap_slippage = avg_exec_price - benchmark_price

        # 执行完成度
        total_executed = sum([e['quantity'] for e in self.executed]) if self.executed else self.total_qty
        completion = total_executed / self.total_qty

        # 价格标准差（执行稳定性）
        price_std = executed_prices.std()

        return {
            'avg_exec_price': avg_exec_price,
            'benchmark': benchmark_price,
            'slippage_bp': vwap_slippage / benchmark_price * 10000,
            'completion_rate': completion,
            'price_std': price_std,
        }

# ===== 使用示例 =====
executor = AlgoExecutor(total_quantity=50000, side='BUY')

# 日内成交量分布（典型U型曲线）
np.random.seed(42)
n_slices = 26  # 每15分钟，6.5小时=26个切片
hourly_pattern = np.array([
    2.0, 1.8, 1.5, 1.2, 1.0, 0.8, 0.7, 0.6, 0.6, 0.7,
    0.8, 0.9, 1.0, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.5,
    1.6, 1.7, 1.8, 1.9, 2.0, 2.2
])
volume_profile = (hourly_pattern * 50000).astype(int)  # 每个时间片的预期市场成交量

# TWAP调度
twap_schedule = executor.twap_schedule(n_slices)
# VWAP调度
vwap_schedule = executor.vwap_schedule(volume_profile, n_slices)

# 对比
print("TWAP vs VWAP 下单计划对比（前10个时间片）:")
print(f"{'时间片':>6} {'TWAP量':>8} {'VWAP量':>8} {'成交量模式':>10}")
for i in range(min(10, n_slices)):
    print(f"{i+1:>6} {twap_schedule[i]:>8} {vwap_schedule[i]:>8} "
          f"{hourly_pattern[i]:>10.1f}x")

# 模拟POV执行
print("\nPOV执行模拟（参与率=5%）:")
executor2 = AlgoExecutor(total_quantity=50000, side='SELL')
total_executed = 0
for i, market_vol in enumerate(volume_profile):
    actual = executor2.pov_execute(market_volume=market_vol, participation_rate=0.05)
    total_executed += actual
    if executor2.remaining <= 0:
        print(f"  已在第{i+1}个时间片完成全部订单")
        break
print(f"  总执行量: {total_executed}")
