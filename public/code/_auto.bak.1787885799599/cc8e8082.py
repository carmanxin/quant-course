# @quantlab/output: cc8e8082
def exchange_flow_analysis(exchange_inflow, exchange_outflow, stablecoin_mcap):
    """
    交易所资金流向综合分析
    """
    net_flow = exchange_outflow - exchange_inflow  # 流出为正

    # 稳定币购买力指标
    btc_price = 50000  # 示例
    stablecoin_buying_power = stablecoin_mcap / btc_price  # 稳定币能买多少BTC

    # 综合分析
    signal_score = 0
    if net_flow > 0:
        signal_score += 1  # 净流出 = 看涨
    else:
        signal_score -= 1

    if stablecoin_mcap.pct_change(7).iloc[-1] > 0.05:
        signal_score += 1  # 稳定币市值上升 = 资金在入场

    return {
        'net_exchange_flow': net_flow,
        'stablecoin_to_btc_ratio': stablecoin_buying_power,
        'composite_signal': signal_score
    }
