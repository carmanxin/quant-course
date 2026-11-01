# @quantlab/output: d2d5ee73
def funding_rate_mean_reversion_strategy(current_rate, rate_history, threshold=2.0):
    """
    基于资金费率均值回归的交易策略
    """
    mean_rate = np.mean(rate_history)
    std_rate = np.std(rate_history)
    z_score = (current_rate - mean_rate) / std_rate

    if z_score > threshold:
        # 费率极高 → 预期回落 → 做空永续 + 做多现货
        signal = 'SHORT_PERP_LONG_SPOT'
        expected_return = current_rate * 3 * 30  # 30天预期费率收入
    elif z_score < -threshold:
        # 费率极低(负值) → 预期回升 → 做多永续 + 做空现货
        signal = 'LONG_PERP_SHORT_SPOT'
        expected_return = abs(current_rate) * 3 * 30
    else:
        signal = 'NEUTRAL'
        expected_return = 0

    return {
        'z_score': z_score,
        'current_rate_annualized': current_rate * 365 * 3 * 100,  # %
        'signal': signal,
        'expected_return_30d_pct': expected_return * 100
    }
