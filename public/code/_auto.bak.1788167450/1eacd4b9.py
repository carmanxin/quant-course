# @quantlab/output: 1eacd4b9
def calculate_network_activity_metrics(tx_df):
    """
    从交易数据计算网络活跃度指标
    """
    tx_df['date'] = tx_df['timeStamp'].dt.date

    daily_stats = tx_df.groupby('date').agg(
        active_senders=('from', 'nunique'),
        active_receivers=('to', 'nunique'),
        tx_count=('hash', 'count'),
        total_volume_eth=('value_eth', 'sum'),
        avg_tx_value_eth=('value_eth', 'mean'),
        median_gas_price=('gasPrice', 'median')
    ).reset_index()

    # 计算趋势
    daily_stats['senders_ma7'] = daily_stats['active_senders'].rolling(7).mean()
    daily_stats['volume_ma7'] = daily_stats['total_volume_eth'].rolling(7).mean()

    return daily_stats
