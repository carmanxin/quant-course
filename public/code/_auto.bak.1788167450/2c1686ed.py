# @quantlab/output: 2c1686ed
def compare_perp_vs_futures(spot_price, perp_price, futures_prices, funding_rate, T, r):
    """
    永续合约与交割合约的持仓成本比较
    futures_prices: dict {expiry: price} 不同到期日的期货价格
    """
    comparison = []

    # 永续合约持仓成本（年化）
    perp_cost = funding_rate * 365 * 3  # 每日3次资金费率结算，年化

    comparison.append({
        'type': '永续合约',
        'price': perp_price,
        'basis_bps': (perp_price / spot_price - 1) * 10000,
        'annualized_cost_pct': perp_cost * 100
    })

    # 各到期日交割合约持仓成本
    for expiry, price in futures_prices.items():
        basis = price / spot_price - 1
        annualized_basis = basis / expiry  # 简化年化
        comparison.append({
            'type': f'期货 ({expiry*12:.0f}个月)',
            'price': price,
            'basis_bps': basis * 10000,
            'annualized_cost_pct': annualized_basis * 100
        })

    return comparison
