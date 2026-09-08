# @quantlab/output: 99a8737f
def vpin_based_risk_control(vpin_current: float,
                            base_spread: float,
                            max_spread: float) -> Tuple[float, float]:
    """
    根据 VPIN 动态调整做市价差和仓位限制。

    参数:
        vpin_current: 当前 VPIN 值
        base_spread: 基础买卖价差
        max_spread: 最大买卖价差
    返回:
        (调整后价差, 仓位缩减比例)
    """
    # VPIN 越高，价差越大，仓位越小
    vpin_clamped = min(vpin_current, 1.0)

    # 价差调整：VPIN 从 0 到 1，价差从 base 到 max
    adjusted_spread = base_spread + (max_spread - base_spread) * vpin_clamped

    # 仓位缩减：VPIN 越高仓位越小
    position_scale = max(0.2, 1.0 - vpin_clamped)

    return adjusted_spread, position_scale
