# @quantlab/output: fa30d21a
def simulate_lp_returns(initial_price, volatility, fee_apr, horizon_days,
                         n_simulations=1000, v2=True, v3_range_multiplier=1.5):
    """
    蒙特卡洛模拟 LP 收益分布
    """
    import numpy as np
    daily_vol = volatility / np.sqrt(365)

    results = []
    for _ in range(n_simulations):
        # 生成价格路径
        returns = np.random.randn(horizon_days) * daily_vol
        price_path = initial_price * np.exp(np.cumsum(returns))
        final_price = price_path[-1]

        if v2:
            # V2: 全区间做市
            P_ratio = final_price / initial_price
            il = impermanent_loss(P_ratio)
        else:
            # V3: 区间内做市
            P_lower = initial_price / v3_range_multiplier
            P_upper = initial_price * v3_range_multiplier

            # 检查价格是否跑出区间
            out_of_range = np.any((price_path < P_lower) | (price_path > P_upper))

            if out_of_range:
                # 简化：价格跑出区间则承受更大的IL
                il = impermanent_loss(final_price / initial_price) * 0.5
            else:
                # 区间内IL更小（资本效率更高）
                il = impermanent_loss(final_price / initial_price) * 0.3

        fee_income = fee_apr * horizon_days / 365
        net_return = fee_income - il
        results.append(net_return)

    results = np.array(results)
    return {
        'mean_return': results.mean(),
        'median_return': np.median(results),
        'std_return': results.std(),
        'win_rate': (results > 0).mean(),
        'var_95': np.percentile(results, 5),
        'sharpe': results.mean() / results.std() if results.std() > 0 else 0
    }

# V2 vs V3 比较
v2_result = simulate_lp_returns(100, 0.80, 0.15, 30, v2=True)
v3_result = simulate_lp_returns(100, 0.80, 0.25, 30, v2=False, v3_range_multiplier=1.5)

print("Uniswap V2 LP 模拟:")
for k, v in v2_result.items():
    print(f"  {k}: {v:.4f}")

print("\nUniswap V3 集中流动性 LP 模拟:")
for k, v in v3_result.items():
    print(f"  {k}: {v:.4f}")
