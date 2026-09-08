# @quantlab/output: 6aaec524
def timestamp_alignment(events: pd.DataFrame,
                         tolerance_ms: int = 100) -> pd.DataFrame:
    """
    对来自不同数据源的异源事件进行时间对齐。

    策略：使用滑动窗口，将容差内的事件视为"同时发生"。

    参数:
        events: 多源事件DataFrame（含 source, timestamp, symbol 列）
        tolerance_ms: 容差（毫秒）
    返回:
        对齐后的事件DataFrame（新增 aligned_ts 列）
    """
    tolerance_ns = pd.Timedelta(milliseconds=tolerance_ms)

    # 对每个 symbol，按时间排序
    aligned_frames = []

    for symbol, group in events.groupby('symbol'):
        group = group.sort_values('timestamp')

        # 将容差内的事件对齐到最早时间
        group['time_diff'] = group['timestamp'].diff()

        # 创建对齐组：当时间差超过容差时，开始新的对齐组
        group['aligned_group'] = (
            group['time_diff'] > tolerance_ns
        ).cumsum()

        # 每个对齐组的时间基准为组内最早时间
        group['aligned_ts'] = group.groupby('aligned_group')['timestamp'] \
            .transform('min')

        aligned_frames.append(group)

    return pd.concat(aligned_frames)
