# @quantlab/output: 2f128f2e
import numpy as np
import pandas as pd
from scipy import stats


class AlphaDecayDetector:
    """Alpha衰减检测器"""

    def __init__(self, strategy_returns: pd.Series, benchmark_returns: pd.Series = None):
        """
        Parameters
        ----------
        strategy_returns : pd.Series
            策略收益率序列
        benchmark_returns : pd.Series, optional
            基准收益率序列
        """
        self.returns = strategy_returns
        self.benchmark = benchmark_returns

    def rolling_alpha(self, window: int = 60) -> pd.Series:
        """计算滚动 Alpha（超额收益的均值）"""
        if self.benchmark is not None:
            excess = self.returns - self.benchmark
        else:
            excess = self.returns

        return excess.rolling(window).mean() * 252  # 年化

    def rolling_sharpe(self, window: int = 60) -> pd.Series:
        """计算滚动夏普比率"""
        excess = self.returns
        if self.benchmark is not None:
            excess = self.returns - self.benchmark

        rolling_mean = excess.rolling(window).mean()
        rolling_std = excess.rolling(window).std()
        return (rolling_mean / rolling_std) * np.sqrt(252)

    def trend_in_alpha(self, window: int = 60) -> dict:
        """检测 Alpha 衰减趋势的统计显著性"""
        rolling_alpha = self.rolling_alpha(window).dropna()

        if len(rolling_alpha) < 30:
            return {'significant_decay': False, 'insufficient_data': True}

        # 对滚动 Alpha 做时间趋势回归
        X = np.arange(len(rolling_alpha))
        y = rolling_alpha.values

        slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

        # 计算年化衰减速度
        decay_per_year = slope * 252

        return {
            'significant_decay': p_value < 0.05 and slope < 0,
            'slope': slope,
            'decay_per_year': decay_per_year,
            'p_value': p_value,
            'r_squared': r_value ** 2,
            'current_alpha': rolling_alpha.iloc[-1],
            'alpha_6m_ago': rolling_alpha.iloc[-min(126, len(rolling_alpha))]
        }

    def estimate_half_life(self) -> float:
        """估算Alpha的半衰期（以年为单位）"""
        result = self.trend_in_alpha()

        if result.get('insufficient_data'):
            return np.inf

        current_alpha = result['current_alpha']
        decay_rate = abs(result['decay_per_year'])

        if decay_rate <= 0 or current_alpha <= 0:
            return np.inf

        # 半衰期 = 当前Alpha / (2 * 衰减速度)
        # 假设线性衰减
        half_life = current_alpha / (2 * decay_rate)
        return half_life
