# @quantlab/output: 841ac4b9
def composite_northbound_dragontiger(
    northbound_signal: pd.DataFrame,
    dragontiger_signal: pd.DataFrame,
    price_data: pd.DataFrame
) -> pd.DataFrame:
    """
    北向资金 + 龙虎榜综合策略

    核心逻辑：
    - 北向资金提供中长期方向信号（2-4周维度）
    - 龙虎榜提供短期催化剂信号（1-5天维度）
    - 两者共振时信号置信度最高
    """
    # 合并信号
    merged = price_data[['date', 'code', 'close']].merge(
        northbound_signal[['date', 'code', 'northbound_signal']],
        on=['date', 'code'], how='left'
    ).merge(
        dragontiger_signal[['date', 'code', 'inst_net_buy', 'inst_buy_ratio']],
        on=['date', 'code'], how='left'
    )

    # 北向信号标准化（截面排序）
    merged['nb_signal_percentile'] = merged.groupby('date')['northbound_signal'].transform(
        lambda x: x.rank(pct=True)
    )

    # 龙虎榜信号（只有上榜的股票有值，填充0）
    merged['dt_signal'] = merged['inst_net_buy'].fillna(0) / merged['close'] * 10000
    merged['dt_signal_percentile'] = merged.groupby('date')['dt_signal'].transform(
        lambda x: np.where(x.sum() > 0, x.rank(pct=True), 0)
    )

    # 综合信号
    merged['composite_signal'] = (
        merged['nb_signal_percentile'].fillna(0.5) * 0.6 +  # 北向权重60%
        merged['dt_signal_percentile'].fillna(0.5) * 0.4    # 龙虎榜权重40%
    )

    # 共振增强：北向和龙虎榜同时强信号
    nb_strong = merged['nb_signal_percentile'] > 0.8
    dt_strong = merged['dt_signal_percentile'] > 0.8

    merged['resonance'] = nb_strong & dt_strong

    # 共振信号加10%的额外权重
    merged.loc[merged['resonance'], 'composite_signal'] *= 1.10
    merged['composite_signal'] = merged['composite_signal'].clip(upper=1.0)

    return merged
