# @quantlab/output: 1111e715
def mbs_price_vs_rate(pool_cf_generator, rates_range):
    """
    MBS 在不同利率情景下的价格模拟 —— 展示负凸度
    pool_cf_generator: 函数(rate)->cashflows
    rates_range: 测试的利率范围
    """
    prices = []
    for r in rates_range:
        cfs = pool_cf_generator(r)
        # 用当前利率折现
        price = sum(cf['total_cashflow'] / (1 + r/12)**cf['month'] for cf in cfs)
        prices.append(price)

    # 计算有效久期和有效凸度
    P0 = prices[len(prices)//2]
    dy = rates_range[1] - rates_range[0]
    duration = -(prices[len(prices)//2 + 1] - prices[len(prices)//2 - 1]) / (2 * P0 * dy)
    convexity = (prices[len(prices)//2 + 1] + prices[len(prices)//2 - 1] - 2*P0) / (P0 * dy**2)

    print(f"有效久期: {duration:.2f}")
    print(f"有效凸度: {convexity:.2f}  {'正凸度' if convexity > 0 else '负凸度⚠️'}")

    return prices
