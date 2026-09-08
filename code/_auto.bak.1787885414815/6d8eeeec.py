# @quantlab/output: 6d8eeeec
# VIX 均值回归策略框架
import pandas as pd

def vix_mean_reversion_signal(vix_current, lookback=20):
    """
    VIX 均值回归信号：
    - VIX 长期均值约为 19-20
    - 超过 30 通常为恐慌状态，适合做多波动率回归
    """
    vix_long_term_mean = 19.5
    vix_std = 8.0
    z_score = (vix_current - vix_long_term_mean) / vix_std

    if z_score > 2.0:
        signal = "SHORT_VOL"  # VIX 极高水平，预期回落
    elif z_score < -1.0:
        signal = "LONG_VOL"   # VIX 极低水平，预期上升
    else:
        signal = "NEUTRAL"

    return {
        'vix': vix_current,
        'z_score': z_score,
        'signal': signal
    }

# 示例
print(vix_mean_reversion_signal(28.5))
