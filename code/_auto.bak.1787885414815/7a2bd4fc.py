# @quantlab/output: 7a2bd4fc
def neutralize_exposure(signal: pd.Series, exposure: pd.Series):
    """因子暴露中性化"""
    from scipy import stats

    # 在截面上对因子暴露做回归，取残差作为中性化后的信号
    mask = signal.notna() & exposure.notna()
    if mask.sum() < 30:
        return signal

    result = stats.linregress(exposure[mask], signal[mask])
    neutralized = signal[mask] - (result.slope * exposure[mask] + result.intercept)

    return pd.Series(neutralized, index=signal[mask].index)
