# @quantlab/output: db5fad0d
import numpy as np
import pandas as pd

def estimate_roll_spread(prices):
    """
    使用Roll模型从交易价格估计有效买卖价差

    prices: 交易价格序列
    """
    # 计算价格变化的协方差
    delta_p = np.diff(prices)

    # Roll公式：S = 2 * sqrt(-Cov(ΔP_t, ΔP_{t-1}))
    # 注意：只有当协方差为负时公式才有意义
    cov = np.cov(delta_p[:-1], delta_p[1:])[0, 1]

    if cov < 0:
        roll_spread = 2 * np.sqrt(-cov)
    else:
        roll_spread = 0
        print("警告：协方差为正，Roll估计不适用")

    return roll_spread

def analyze_transaction_costs(prices, volumes):
    """
    综合分析交易数据中的成本指标
    """
    df = pd.DataFrame({'price': prices, 'volume': volumes})
    df['return'] = df['price'].pct_change()
    df['direction'] = np.sign(df['return'])

    # 1. Roll价差
    roll_spread = estimate_roll_spread(prices)

    # 2. 价格反转度量（买卖压力）
    df['reversal'] = -df['return'].shift(-1) * df['direction']
    effective_cost = df['reversal'].mean()

    # 3. Amihud非流动性指标
    df['amihud'] = np.abs(df['return']) / (df['volume'] * df['price'])
    amihud_illiquidity = df['amihud'].mean()

    results = {
        'roll_spread': roll_spread,
        'roll_spread_bps': roll_spread / np.mean(prices) * 10000,
        'effective_cost_bps': effective_cost * 10000,
        'amihud_illiquidity': amihud_illiquidity,
        'avg_daily_volume': np.mean(volumes)
    }

    print("=== 微观结构分析 ===")
    for k, v in results.items():
        if 'bps' in k:
            print(f"{k}: {v:.2f} bps")
        else:
            print(f"{k}: {v:.6f}")

    return results

# 使用示例
# prices = df['Close'].values
# volumes = df['Volume'].values
# results = analyze_transaction_costs(prices, volumes)
