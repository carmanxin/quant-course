# @quantlab/output: 566bcb35
def calculate_mvrv(market_cap_series, realized_cap_series):
    """
    计算 MVRV 比率
    MVRV > 3.7 通常为顶部区域
    MVRV < 1.0 通常为底部区域（累积区）
    """
    mvrv = market_cap_series / realized_cap_series

    signals = pd.Series('neutral', index=mvrv.index)
    signals[mvrv > 3.7] = 'overvalued_extreme'
    signals[mvrv > 2.5] = 'overvalued'
    signals[mvrv < 1.0] = 'undervalued_extreme'
    signals[mvrv < 1.5] = 'undervalued'

    return pd.DataFrame({
        'mvrv': mvrv,
        'signal': signals
    })
