# @quantlab/output: 9580aca9
def calculate_nvt_ratio(market_cap, daily_tx_volume, window=90):
    """
    计算 NVT 比率和 NVT Signal
    market_cap: Series, 每日市值
    daily_tx_volume: Series, 每日链上交易量（USD计）
    """
    tx_volume_ma = daily_tx_volume.rolling(window).mean()
    nvt = market_cap / tx_volume_ma

    # NVT Signal（标准化）
    nvt_ma = nvt.rolling(window).mean()
    nvt_std = nvt.rolling(window).std()
    nvt_zscore = (nvt - nvt_ma) / nvt_std

    return pd.DataFrame({
        'nvt': nvt,
        'nvt_ma': nvt_ma,
        'nvt_zscore': nvt_zscore,
        'overvalued': nvt_zscore > 2.0,
        'undervalued': nvt_zscore < -2.0
    })
