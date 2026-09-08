# @quantlab/output: 556beab6
import numpy as np

class CUSUMDetector:
    """CUSUM检测器 - 监测策略PnL是否发生结构性恶化"""

    def __init__(self, target_mean=0.001, drift=0.0005, threshold=0.05):
        """
        target_mean: 预期每日收益率均值（零假设）
        drift: 最小可检测偏移（备择假设）
        threshold: 判定阈值
        """
        self.target_mean = target_mean
        self.drift = drift
        self.threshold = threshold
        self.c_plus = 0.0
        self.c_minus = 0.0
        self.alarm_count = 0

    def update(self, daily_return):
        """输入每日收益，检查是否有偏移"""
        # 标准化
        x = daily_return
        K = self.drift / 2

        # CUSUM更新
        self.c_plus = max(0, self.c_plus + x - self.target_mean - K)
        self.c_minus = max(0, self.c_minus - x + self.target_mean - K)

        # 检查是否超过阈值
        if self.c_plus > self.threshold:
            self.alarm_count += 1
            self.c_plus = 0  # 重置
            return 'UPWARD_SHIFT'  # 正向偏移（好事？）
        elif self.c_minus > self.threshold:
            self.alarm_count += 1
            self.c_minus = 0  # 重置
            return 'DOWNWARD_SHIFT'  # 负向偏移（坏事！）

        return 'OK'

    def get_status(self):
        return {
            'c_plus': self.c_plus,
            'c_minus': self.c_minus,
            'total_alarms': self.alarm_count
        }

# 模拟检测
np.random.seed(42)
detector = CUSUMDetector(target_mean=0.001, drift=0.0005, threshold=0.03)

# 模拟策略正常的PnL流
normal_returns = np.random.normal(0.001, 0.01, 40)

# 模拟策略恶化后的PnL流
deteriorated_returns = np.random.normal(-0.001, 0.015, 40)

print("CUSUM策略偏移检测:")
for phase, returns in [("正常期", normal_returns), ("恶化期", deteriorated_returns)]:
    print(f"\n{phase}:")
    for i, ret in enumerate(returns):
        result = detector.update(ret)
        if result != 'OK':
            print(f"  第{i+1}天: 检测到 {result} "
                  f"(C+={detector.c_plus:.4f}, C-={detector.c_minus:.4f})")
