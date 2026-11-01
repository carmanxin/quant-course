# @quantlab/output: 02dc9eaf
def cross_exchange_funding_arb(exchanges_data, min_spread_bps=5):
    """
    跨交易所资金费率套利扫描
    exchanges_data: dict {exchange_name: {'perp_price': ..., 'funding_rate': ...}}
    min_spread_bps: 最小套利触发价差（基点）
    """
    opportunities = []
    names = list(exchanges_data.keys())

    for i in range(len(names)):
        for j in range(i+1, len(names)):
            ex1, ex2 = names[i], names[j]
            d1, d2 = exchanges_data[ex1], exchanges_data[ex2]

            # 计算调整后的套利收益
            # 在费率低的所做多，费率高的所做空
            if d1['funding_rate'] > d2['funding_rate']:
                long_ex, short_ex = ex2, ex1
                funding_spread = d1['funding_rate'] - d2['funding_rate']
            else:
                long_ex, short_ex = ex1, ex2
                funding_spread = d2['funding_rate'] - d1['funding_rate']

            # 价格基差（做多价格 - 做空价格）
            price_spread = exchanges_data[long_ex]['perp_price'] - exchanges_data[short_ex]['perp_price']
            price_spread_bps = price_spread / exchanges_data[short_ex]['perp_price'] * 10000

            # 总预期收益（不包括交易成本）
            # 包括价格收敛的收益 + 资金费率差收入
            total_spread_bps = funding_spread * 10000 + price_spread_bps

            if total_spread_bps > min_spread_bps:
                opportunities.append({
                    'long_exchange': long_ex,
                    'short_exchange': short_ex,
                    'funding_spread_annualized': funding_spread,
                    'price_spread_bps': price_spread_bps,
                    'total_spread_bps': total_spread_bps
                })

    return sorted(opportunities, key=lambda x: x['total_spread_bps'], reverse=True)
