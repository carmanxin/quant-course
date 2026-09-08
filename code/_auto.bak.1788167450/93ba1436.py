# @quantlab/output: 93ba1436
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint, adfuller
from scipy import stats

def find_cointegrated_pairs(prices_df, p_threshold=0.05):
    """
    在全市场中寻找协整配对
    prices_df: 每列是一只股票的价格序列
    """
    n = prices_df.shape[1]
    pairs = []
    pvalues = []

    for i in range(n):
        for j in range(i+1, n):
            score, pvalue, _ = coint(prices_df.iloc[:, i], prices_df.iloc[:, j])
            if pvalue < p_threshold:
                pairs.append((prices_df.columns[i], prices_df.columns[j]))
                pvalues.append(pvalue)

    # 按p值排序，返回最优配对
    sorted_idx = np.argsort(pvalues)
    return [(pairs[i], pvalues[i]) for i in sorted_idx]

def generate_pair_signal(stock1_prices, stock2_prices, lookback=60, entry_z=2.0):
    """
    生成配对交易信号
    """
    # 滚动OLS估计对冲比率
    hedge_ratios = []
    for t in range(lookback, len(stock1_prices)):
        y = stock1_prices[t-lookback:t]
        x = stock2_prices[t-lookback:t]
        x_with_const = np.column_stack([np.ones(len(x)), x])
        beta = np.linalg.lstsq(x_with_const, y, rcond=None)[0]
        hedge_ratios.append(beta[1])

    hedge_ratios = np.array(hedge_ratios)

    # 计算价差
    spread = stock1_prices[lookback:] - hedge_ratios * stock2_prices[lookback:]

    # 标准化价差
    spread_mean = pd.Series(spread).rolling(lookback).mean()
    spread_std = pd.Series(spread).rolling(lookback).std()
    zscore = (spread - spread_mean) / spread_std

    # 生成信号
    signal = np.zeros(len(zscore))
    signal[zscore > entry_z] = -1  # 做空价差（卖1买2）
    signal[zscore < -entry_z] = 1  # 做多价差（买1卖2）

    # 平仓信号：价差回归均值
    signal[np.abs(zscore) < 0.5] = 0

    return signal, zscore, spread
