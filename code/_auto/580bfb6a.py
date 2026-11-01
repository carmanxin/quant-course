# @quantlab/output: 580bfb6a
def merger_arbitrage_spread(target_price, acquirer_price, offer_price,
                            offer_ratio, deal_type='cash'):
    """
    计算并购套利的价差

    Parameters:
        target_price: 目标公司当前股价
        acquirer_price: 收购方当前股价
        offer_price: 收购报价（每股）
        offer_ratio: 换股比例（如果是股票交易）
        deal_type: 'cash'（现金收购）或 'stock'（股票收购）
    """
    if deal_type == 'cash':
        # 现金收购：价差 = 报价 - 目标股价
        spread = (offer_price / target_price - 1) * 100
    elif deal_type == 'stock':
        # 股票收购：价差 = 收购方股价 * 换股比例 - 目标股价
        implied_value = acquirer_price * offer_ratio
        spread = (implied_value / target_price - 1) * 100
    else:
        raise ValueError(f"Unknown deal_type: {deal_type}")

    return spread

def track_merger_arbitrage(deals_data, price_data):
    """
    追踪多个并购套利机会

    deals_data: DataFrame with columns [target, acquirer, offer_price, offer_ratio,
                 deal_type, announce_date, expected_close_date]
    """
    spreads = {}
    for _, deal in deals_data.iterrows():
        target = deal['target']
        acquirer = deal['acquirer']

        if target not in price_data.columns or acquirer not in price_data.columns:
            continue

        spread = merger_arbitrage_spread(
            target_price=price_data[target],
            acquirer_price=price_data[acquirer],
            offer_price=deal['offer_price'],
            offer_ratio=deal['offer_ratio'],
            deal_type=deal['deal_type']
        )

        # 年化收益率 = 价差 / (预期完成天数 / 365)
        days_to_close = (deal['expected_close_date'] - price_data.index).days
        annualized_return = spread / (days_to_close / 365)

        spreads[target] = {
            'spread': spread,
            'annualized_return': annualized_return,
            'days_to_close': days_to_close
        }

    return pd.DataFrame(spreads).T
