# @quantlab/output: 79e1d850
def bei_momentum_signal(bei_time_series: pd.Series,
                         short_window: int = 5,
                         long_window: int = 20) -> float:
    """
    BEI 动量信号。

    正值表示通胀预期上升动能，建议做多通胀敏感资产；
    负值表示通胀预期下降动能。

    参数:
        bei_time_series: BEI 时间序列（如10年期）
        short_window: 短期窗口（天）
        long_window: 长期窗口（天）
    返回:
        信号值 [-1, 1]
    """
    short_ma = bei_time_series.rolling(short_window).mean()
    long_ma = bei_time_series.rolling(long_window).mean()

    # 短均线 - 长均线，标准化
    raw_signal = (short_ma.iloc[-1] - long_ma.iloc[-1]) / \
                 bei_time_series.rolling(long_window).std().iloc[-1]

    # 限制在 [-2, 2]，然后映射到 [-1, 1]
    signal = np.clip(raw_signal / 2, -1, 1)

    return signal
