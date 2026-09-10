# @quantlab/output: 75ec9521
def effective_duration(price_function, P0, y0, dy=0.0001):
    """
    通过数值扰动计算有效久期
    price_function(y): 给定收益率y，返回模型价格
    """
    P_down = price_function(y0 - dy)
    P_up = price_function(y0 + dy)
    duration = (P_down - P_up) / (2 * P0 * dy)
    return duration
