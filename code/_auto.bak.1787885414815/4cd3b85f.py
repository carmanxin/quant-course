# @quantlab/output: 4cd3b85f
def whale_behavior_analysis(large_tx_df, exchange_wallets, threshold_btc=100):
    """
    巨鲸行为分析
    """
    # 识别大额转账
    whale_txs = large_tx_df[large_tx_df['value_btc'] >= threshold_btc]

    # 计算流入交易所的鲸鱼交易比例
    whale_to_exchange = whale_txs[whale_txs['to'].isin(exchange_wallets)]
    inflow_ratio = len(whale_to_exchange) / len(whale_txs)

    # 净流量分析
    net_flow_to_exchanges = (
        whale_txs[whale_txs['to'].isin(exchange_wallets)]['value_btc'].sum()
        - whale_txs[whale_txs['from'].isin(exchange_wallets)]['value_btc'].sum()
    )

    return {
        'whale_tx_count': len(whale_txs),
        'whale_exchange_inflow_ratio': inflow_ratio,
        'whale_net_flow_btc': net_flow_to_exchanges,
        'signal': 'bearish' if inflow_ratio > 0.6 and net_flow_to_exchanges > 0 else 'neutral'
    }
