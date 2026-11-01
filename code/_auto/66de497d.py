# @quantlab/output: 66de497d
def avellaneda_stoikov_quotes(inventory: float,
                                reference_price: float,
                                T_remaining: float,
                                gamma: float,
                                sigma: float,
                                k: float,
                                A: float) -> Tuple[float, float, float, float]:
    """
    Avellaneda-Stoikov(2008) 最优做市报价。

    参数:
        inventory: 当前库存
        reference_price: 参考价格
        T_remaining: 剩余交易时间
        gamma: 风险厌恶参数
        sigma: 波动率
        k: 订单到达率参数
        A: 订单到达率缩放参数
    返回:
        (reservation_bid, reservation_ask, bid_quote, ask_quote)
    """
    # 保留价格
    reservation_price = reference_price - inventory * gamma * sigma ** 2 * T_remaining

    # 最优价差
    optimal_spread = gamma * sigma ** 2 * T_remaining + \
        2 / gamma * np.log(1 + gamma / k)

    # 报价
    bid_quote = reservation_price - optimal_spread / 2
    ask_quote = reservation_price + optimal_spread / 2

    # 确保不交叉
    bid_quote = min(bid_quote, reference_price)
    ask_quote = max(ask_quote, reference_price)

    return reservation_price - optimal_spread / 2, \
        reservation_price + optimal_spread / 2, \
        bid_quote, ask_quote
