# @quantlab/output: 0c92bc3b
# 流动性指标示例
def bidask_spread_metrics(spread_grid):
    """价差统计函数 (单位: 最小变动单位)"""
    avg_spread = np.mean(spread_grid)
    max_spread = np.max(spread_grid)
    eff_spread = np.mean(spread_grid) * 0.5  # 有效价差
    return avg_spread, eff_spread, max_spread

# 50ETF ATM 主力合约(3 月) 5 天平均 bid-ask
spreads = [1, 1, 2, 1, 2, 1, 1]  # 最小变动倍数
avg, eff, mx = bidask_spread_metrics(spreads)
print(f"50ETF 主力 ATM 期权:")
print(f"  平均价差: {avg} ticks (1 tick = 0.0001 元 = 1元/张)")
print(f"  有效价差: {eff} ticks")
print(f"  最大价差: {mx} ticks")
