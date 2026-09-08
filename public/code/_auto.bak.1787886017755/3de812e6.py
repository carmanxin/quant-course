# @quantlab/output: 3de812e6
def nonlinear_temporary_impact(v: float,
                                eta: float,
                                depth: float,
                                exponent: float = 1.5) -> float:
    """
    非线性临时冲击函数，反映订单簿深度约束。

    参数:
        v: 执行速率
        eta: 基础冲击系数
        depth: 订单簿参考深度
        exponent: 非线性指数（通常 1.3-2.0）
    """
    return eta * v * (1 + (abs(v) / depth) ** (exponent - 1))
