# @quantlab/output: e282d981
def optimal_spread(alpha: float,  # 知情交易者比例
                   price_range: float,  # 价值不确定范围
                   base_spread: float = 0.01,  # 基础运营成本
                   competition: float = 0.5) -> float:
    """
    计算最优买卖价差

    Parameters
    ----------
    alpha : float
        知情交易者的概率
    price_range : float
        做市商对价值的不确定区间
    base_spread : float
        覆盖运营成本的基础价差
    competition : float
        竞争程度（0-1，越高价差越小）
    """
    adverse_selection_cost = alpha * price_range
    optimal = (2 * adverse_selection_cost + base_spread) / (1 - competition)
    return max(base_spread, optimal)


# 示例
print(f"高知情交易(alpha=0.3): spread = {optimal_spread(0.3, 0.10):.4f}")
print(f"低知情交易(alpha=0.1): spread = {optimal_spread(0.1, 0.10):.4f}")
print(f"高竞争(comp=0.8): spread = {optimal_spread(0.2, 0.10, competition=0.8):.4f}")
