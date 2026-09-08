# @quantlab/output: f282c4f3
def uniswap_v3_position(amount_x, amount_y, P_current, P_lower, P_upper):
    """
    Uniswap V3 流动性头寸计算
    amount_x: 提供的资产X数量
    amount_y: 提供的资产Y数量
    P_current: 当前价格
    P_lower: 做市价格下限
    P_upper: 做市价格上限
    """
    sqrtP = np.sqrt(P_current)
    sqrtPa = np.sqrt(P_lower)
    sqrtPb = np.sqrt(P_upper)

    # 计算流动性 L
    if P_current <= P_lower:
        # 全仓资产 X
        L = amount_x * (sqrtP * sqrtPb) / (sqrtPb - sqrtP)
    elif P_current >= P_upper:
        # 全仓资产 Y
        L = amount_y / (sqrtP - sqrtPa)
    else:
        # 两种资产都有
        L_x = amount_x * (sqrtP * sqrtPb) / (sqrtPb - sqrtP)
        L_y = amount_y / (sqrtP - sqrtPa)
        L = min(L_x, L_y)

    # 计算区间内的实际资产数量
    if P_current <= P_lower:
        x_real = amount_x
        y_real = 0
    elif P_current >= P_upper:
        x_real = 0
        y_real = amount_y
    else:
        x_real = L * (sqrtPb - sqrtP) / (sqrtP * sqrtPb)
        y_real = L * (sqrtP - sqrtPa)

    return {
        'liquidity': L,
        'x_real': x_real,
        'y_real': y_real,
        'position_value': x_real * P_current + y_real,
        'capital_efficiency': (x_real * P_current + y_real) / (amount_x * P_current + amount_y)
    }

# 示例：在 ETH=2000 USDC 的价格下做市
pos = uniswap_v3_position(
    amount_x=1,     # 1 ETH
    amount_y=2000,  # 2000 USDC
    P_current=2000,
    P_lower=1800,
    P_upper=2200
)
print(f"流动性: {pos['liquidity']:.2f}")
print(f"资金效率: {pos['capital_efficiency']:.2%}")
