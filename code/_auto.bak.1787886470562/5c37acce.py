# @quantlab/output: 5c37acce
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

class PairsTrader:
    def __init__(self, lookback=60, entry_z=2.0, exit_z=0.5, min_half_life=1, max_half_life=30):
        """
        Parameters:
            lookback: 用于估计对冲比率和价差统计的回看窗口
            entry_z: 入场Z-score阈值
            exit_z: 出场Z-score阈值
            min_half_life: 可接受的最短半衰期（天）
            max_half_life: 可接受的最长半衰期（天）
        """
        self.lookback = lookback
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.min_half_life = min_half_life
        self.max_half_life = max_half_life

    def estimate_hedge_ratio(self, price_a, price_b):
        """用滚动窗口回归估计对冲比率"""
        y = price_a.values
        X = np.column_stack([np.ones(len(price_b)), price_b.values])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        return beta[0], beta[1]  # intercept, hedge_ratio

    def compute_half_life(self, spread):
        """估计价差的均值回归半衰期"""
        spread_lag = spread.shift(1)
        spread_diff = spread - spread_lag
        spread_lag = spread_lag.dropna()
        spread_diff = spread_diff.dropna()

        # OLS: spread_t - spread_{t-1} = gamma * spread_{t-1} + const
        X = np.column_stack([np.ones(len(spread_lag)), spread_lag.values])
        y = spread_diff.values

        if len(X) < 10:
            return np.inf

        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        theta = beta[1] + 1  # AR(1)系数

        if theta <= 0:
            return np.inf

        half_life = -np.log(2) / np.log(theta)
        return min(half_life, 1e6)  # 防止无穷大

    def generate_signals(self, price_a, price_b):
        """生成配对交易信号"""
        # 滚动估计
        alpha, hedge_ratio = self.estimate_hedge_ratio(
            price_a.iloc[:self.lookback], price_b.iloc[:self.lookback]
        )

        # 计算全期价差
        spread = price_a - hedge_ratio * price_b

        # 检查协整性
        _, p_value, _ = coint(price_a, price_b)
        if p_value > 0.05:
            return pd.Series(0, index=price_a.index), {'coint_pvalue': p_value}

        # 检查半衰期
        spread_hist = spread.iloc[:self.lookback]
        half_life = self.compute_half_life(spread_hist)
        if half_life < self.min_half_life or half_life > self.max_half_life:
            return pd.Series(0, index=price_a.index), {'half_life': half_life}

        # 计算滚动Z-score
        rolling_mean = spread.rolling(self.lookback).mean()
        rolling_std = spread.rolling(self.lookback).std()
        zscore = (spread - rolling_mean) / rolling_std

        # 生成信号：均值回归方向
        signals = pd.Series(0, index=price_a.index)
        signals[zscore < -self.entry_z] = 1   # 价差过低，做多spread
        signals[zscore > self.entry_z] = -1   # 价差过高，做空spread

        # 出场信号：Z-score回到阈值内
        signals[abs(zscore) < self.exit_z] = 0

        return signals, {'coint_pvalue': p_value, 'half_life': half_life}
