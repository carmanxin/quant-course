# @quantlab/output: 773e3cfd
def signal_driven_spread(base_spread: float,
                          volatility: float,
                          order_imbalance: float,
                          vpin: float,
                          time_of_day_factor: float,
                          inventory_ratio: float) -> float:
    """
    多维信号驱动的动态价差调整。

    参数:
        base_spread: 基础价差（tick的倍数）
        volatility: 当前波动率与历史均值的比率
        order_imbalance: 订单簿不平衡指标 [-1, 1]
        vpin: 订单流毒性指标 [0, 1]
        time_of_day_factor: 日内时间因子 (0=开盘/收盘, 1=盘中)
        inventory_ratio: 库存/最大库存比率 [0, 1]
    返回:
        调整后的价差
    """
    # 各信号的调整系数
    vol_adj = 1.0 + (volatility - 1.0) * 0.5      # 波动率高 -> 加大价差
    tox_adj = 1.0 + vpin * 1.5                      # 毒性高 -> 加大价差
    imbalance_adj = 1.0 + abs(order_imbalance) * 0.3 # 不平衡 -> 加大价差
    tod_adj = 1.0 + (1 - time_of_day_factor) * 0.5  # 开盘/收盘 -> 加大价差
    inv_adj = 1.0 + inventory_ratio * 1.0           # 库存高 -> 加大价差

    adjusted_spread = base_spread * (
        vol_adj * tox_adj * imbalance_adj * tod_adj * inv_adj
    ) ** (1.0 / 5.0)  # 几何平均

    return max(base_spread * 0.8, min(adjusted_spread, base_spread * 3.0))
