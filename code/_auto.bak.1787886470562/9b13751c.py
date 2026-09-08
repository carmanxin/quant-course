# @quantlab/output: 9b13751c
import numpy as np
import pandas as pd
from enum import Enum
from typing import Tuple

class MarketRegime(Enum):
    MEAN_REVERTING = 1
    TRENDING = 2
    NEUTRAL = 3

def detect_market_regime(prices: np.ndarray,
                          window: int = 100) -> MarketRegime:
    """
    检测市场状态：均值回归 vs 趋势市场。

    使用 Hurst 指数和自相关结构来分类。
    """
    # 1. 计算 Hurst 指数（简化版：方差比检验）
    def hurst_estimate(ts, max_lag=20):
        lags = range(2, max_lag)
        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag])))
               for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0]

    # 2. 自相关
    returns = np.diff(prices[-window:]) / prices[-window-1:-1]
    autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]

    # 3. 趋势强度（趋势占比）
    trend_strength = np.mean(returns) / (np.std(returns) + 1e-10) * np.sqrt(252)

    if abs(trend_strength) > 1.5 and abs(autocorr) > 0.1:
        return MarketRegime.TRENDING
    elif abs(autocorr) < 0.05 and abs(trend_strength) < 0.5:
        return MarketRegime.MEAN_REVERTING
    else:
        return MarketRegime.NEUTRAL


def adaptive_inventory_control(inventory: float,
                                max_inventory: float,
                                mid_price: float,
                                vwap_entry: float,
                                regime: MarketRegime) -> dict:
    """
    基于市场状态的适应性库存控制。

    参数:
        inventory: 当前净头寸（正=多头，负=空头）
        max_inventory: 最大允许头寸
        mid_price: 当前中间价
        vwap_entry: 加权平均入场价
        regime: 市场状态
    返回:
        包含 inventory_ratio, skew_bps, hedge_urgency 的字典
    """
    inventory_ratio = abs(inventory) / max_inventory
    pnl_bps = (mid_price - vwap_entry) / vwap_entry * 10000 if inventory != 0 else 0

    if regime == MarketRegime.MEAN_REVERTING:
        # 均值回归：较大的库存容忍度
        skew_bps = -inventory_ratio * 0.5  # 轻度偏斜
        hedge_urgency = max(0, inventory_ratio - 0.8)
    elif regime == MarketRegime.TRENDING:
        # 趋势市场：严格控制库存
        skew_bps = -np.sign(inventory) * inventory_ratio * 2.0  # 强偏斜
        hedge_urgency = max(0, inventory_ratio - 0.3)
    else:
        # 中性市场
        skew_bps = -inventory_ratio * 1.0
        hedge_urgency = max(0, inventory_ratio - 0.5)

    return {
        'inventory_ratio': inventory_ratio,
        'skew_bps': skew_bps,
        'hedge_urgency': hedge_urgency,
        'unrealized_pnl_bps': pnl_bps if inventory != 0 else 0
    }
