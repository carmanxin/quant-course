# @quantlab/output: 5a60cfc9
def compute_vpin(df: pd.DataFrame,
                 volume_bucket_size: int,
                 n_buckets: int = 50) -> pd.Series:
    """
    计算 VPIN 指标。

    参数:
        df: 已标注买卖方向的 tick 数据
        volume_bucket_size: 每个体积桶的成交量（如 10000 股）
        n_buckets: 用于计算 VPIN 的桶数量
    返回:
        VPIN 时间序列
    """
    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # 按成交量累积
    buckets = []
    cum_vol = 0
    bucket_buy = 0
    bucket_sell = 0
    bucket_times = []

    for idx, row in df.iterrows():
        cum_vol += row['volume']

        if row['trade_direction'] == 1:
            bucket_buy += row['volume']
            bucket_sell -= 0  # 保持语义清晰
        else:
            bucket_sell += row['volume']

        # 体积桶填满时记录
        if cum_vol >= volume_bucket_size:
            excess = cum_vol - volume_bucket_size # 按比例分配超额部分
            if row['trade_direction'] == 1:
                bucket_buy -= excess
            else:
                bucket_sell -= excess

            # 计算该桶的订单不平衡
            oi = abs(bucket_buy - bucket_sell) / volume_bucket_size
            buckets.append({
                'time': idx,
                'OI': oi
            })

            # 重置，保留超额部分
            cum_vol = excess
            bucket_buy = excess if row['trade_direction'] == 1 else 0
            bucket_sell = excess if row['trade_direction'] == -1 else 0

    bucket_df = pd.DataFrame(buckets)
    bucket_df.set_index('time', inplace=True)

    # 滚动计算 VPIN
    bucket_df['VPIN'] = bucket_df['OI'].rolling(window=n_buckets).mean()

    return bucket_df['VPIN']
