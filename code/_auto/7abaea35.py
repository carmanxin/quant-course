# @quantlab/output: 7abaea35
import numpy as np

def uniswap_v2_swap(x, y, dx, fee=0.003):
    """
    Uniswap V2 交易计算
    x: 池中资产 X 的数量
    y: 池中资产 Y 的数量
    dx: 输入资产 X 的数量
    fee: 手续费率 (0.3%)
    返回：获得的资产 Y 数量，有效成交价格
    """
    dx_after_fee = dx * (1 - fee)
    dy = (y * dx_after_fee) / (x + dx_after_fee)
    effective_price = dx / dy  # 实际成交价格

    # 新状态
    new_x = x + dx
    new_y = y - dy
    new_price = new_x / new_y  # 新边际价格

    return {
        'amount_out': dy,
        'effective_price': effective_price,
        'new_marginal_price': new_price,
        'price_impact': (effective_price - x / y) / (x / y)
    }

# 示例：用100 USDC 在 ETH-USDC 池中买入 ETH
pool_usdc = 1000000
pool_eth = 500
amount_in = 100  # USDC

result = uniswap_v2_swap(pool_usdc, pool_eth, amount_in)
print(f"获得 ETH: {result['amount_out']:.6f}")
print(f"成交价格: ${result['effective_price']:.2f} per ETH")
print(f"价格冲击: {result['price_impact']*100:.4f}%")
