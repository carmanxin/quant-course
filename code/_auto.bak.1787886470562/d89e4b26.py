# @quantlab/output: d89e4b26
def key_rate_duration(price_function, key_maturities, y0, dy=0.0001):
    """
    计算关键利率久期
    price_function(spots_dict): 输入各期限的即期利率，返回模型价格
    key_maturities: 关键期限列表 [2, 5, 10, 30]
    """
    P0 = price_function({m: y0 for m in key_maturities})
    krds = {}

    for k in key_maturities:
        # 仅扰动特定期限，其他期限保持不变或插值
        spots_up = {m: y0 + (dy if m == k else 0) for m in key_maturities}
        spots_down = {m: y0 + (-dy if m == k else 0) for m in key_maturities}

        P_up = price_function(spots_up)
        P_down = price_function(spots_down)

        krds[k] = -(P_up - P_down) / (2 * P0 * dy)

    return krds
