# @quantlab/output: 9732225f
import pandas as pd
import numpy as np

def factor_computation_pipeline(prices_df, volumes_df=None, market_cap_df=None):
    """
    一个典型的因子计算流水线，展示Pandas在量化中的核心用法

    prices_df: DataFrame, index=日期, columns=股票代码, values=收盘价
    volumes_df: DataFrame, 同上, values=成交量
    market_cap_df: DataFrame, 同上, values=总市值
    """
    # === 收益率计算 ===
    daily_returns = prices_df.pct_change()  # 日收益率

    # === 动量因子 ===
    momentum_1m = prices_df / prices_df.shift(21) - 1   # 1个月动量（~21个交易日）
    momentum_3m = prices_df / prices_df.shift(63) - 1   # 3个月动量
    momentum_12m = prices_df / prices_df.shift(252) - 1  # 12个月动量
    momentum_12_1m = momentum_12m - momentum_1m           # 12-1月动量（剔除短期反转）

    # === 波动率因子 ===
    volatility_1m = daily_returns.rolling(21).std() * np.sqrt(252)  # 年化波动率
    volatility_3m = daily_returns.rolling(63).std() * np.sqrt(252)

    # === 换手率因子 ===
    if volumes_df is not None:
        turnover_1m = volumes_df.rolling(21).mean()  # 日均成交量
        turnover_ratio = volumes_df / volumes_df.rolling(252).mean()  # 相对换手率

    # === 流动性因子 (Amihud) ===
    if volumes_df is not None:
        amihud = (daily_returns.abs() / (volumes_df * prices_df)).rolling(21).mean()

    # === 横截面标准化 ===
    # 将每个日期的所有股票因子值标准化为均值0标准差1
    def cross_sectional_zscore(factor_df):
        return factor_df.sub(factor_df.mean(axis=1), axis=0).div(factor_df.std(axis=1), axis=0)

    # 对动量因子做横截面标准化
    mom_1m_z = cross_sectional_zscore(momentum_1m)
    vol_1m_z = cross_sectional_zscore(volatility_1m)

    # === 合并多个因子（等权合成） ===
    composite = (mom_1m_z + (-vol_1m_z)) / 2  # 高动量 + 低波动

    # === 处理缺失值 ===
    composite = composite.replace([np.inf, -np.inf], np.nan)

    # 前向填充缺失值（停牌日沿用前值）
    composite = composite.ffill(limit=5)  # 最多填充5天

    # 极端值处理 (Winsorize at 1% and 99%)
    lower = composite.quantile(0.01, axis=1)
    upper = composite.quantile(0.99, axis=1)
    composite = composite.clip(lower, upper, axis=0)

    return {
        'momentum_1m': momentum_1m,
        'momentum_12_1m': momentum_12_1m,
        'volatility_1m': volatility_1m,
        'composite': composite,
        'daily_returns': daily_returns
    }

# 使用示例
# factors = factor_computation_pipeline(prices_df, volumes_df)
