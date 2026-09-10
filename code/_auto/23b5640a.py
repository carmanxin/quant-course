# @quantlab/output: 23b5640a
def compute_crowding_composite(sector_data: pd.DataFrame) -> pd.DataFrame:
    """
    计算行业拥挤度综合指标

    返回拥挤度分数：0-1之间，1表示极度拥挤
    """
    crowding = pd.DataFrame(index=sector_data.index, columns=sector_data.columns)

    for sector in sector_data.columns:
        sector_df = sector_data[sector]

        # 1. 成交额占比拥挤度
        if 'amount_pct' in sector_df:
            amount_percentile = sector_df['amount_pct'].rolling(252).apply(
                lambda x: stats.percentileofscore(x, x.iloc[-1]) / 100
            )
            crowding[sector] = amount_percentile * 0.3

        # 2. 换手率拥挤度
        if 'turnover' in sector_df:
            turnover_ma = sector_df['turnover'].rolling(20).mean()
            turnover_hist_ma = sector_df['turnover'].rolling(252).mean()

            # 当换手率显著高于历史平均时，拥挤度高
            turnover_ratio = turnover_ma / turnover_hist_ma
            crowding[sector] = crowding[sector].fillna(0) + \
                               turnover_ratio.clip(0, 3) / 3 * 0.25

        # 3. 收益率拥挤度（连续阳线天数）
        if 'return' in sector_df:
            consecutive_up = (sector_df['return'] > 0).astype(int)
            streak = consecutive_up * (consecutive_up.groupby(
                (consecutive_up != consecutive_up.shift()).cumsum()
            ).cumcount() + 1)

            # 连续上涨超过5天，拥挤度上升
            streak_score = (streak / 10).clip(0, 1)
            crowding[sector] = crowding[sector].fillna(0) + streak_score * 0.20

        # 4. 波动率拥挤度
        if 'return' in sector_df:
            vol = sector_df['return'].rolling(20).std()
            vol_hist = sector_df['return'].rolling(252).std()
            vol_ratio = vol / vol_hist
            crowding[sector] = crowding[sector].fillna(0) + \
                               vol_ratio.clip(0, 3) / 3 * 0.25

    return crowding.clip(0, 1)  # 确保在 0-1 之间
