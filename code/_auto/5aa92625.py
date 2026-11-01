# @quantlab/output: 5aa92625
def stress_test_scenarios():
    """用合成数据构造历史未发生的极端场景"""

    scenarios = {
        '正常市场(基线)': {
            'mu': 0.0004, 'sigma': 0.015,
            'jump_lambda': 0.0,
        },
        '高波动率(震荡市)': {
            'mu': 0.0002, 'sigma': 0.03,
            'jump_lambda': 0.0,
        },
        '低波动率(慢牛市)': {
            'mu': 0.0006, 'sigma': 0.008,
            'jump_lambda': 0.0,
        },
        '频繁黑天鹅': {
            'mu': 0.0003, 'sigma': 0.012,
            'jump_lambda': 0.20,  # 年化 20% 概率
            'jump_mu': -0.08,    # 平均跌 8%
            'jump_sigma': 0.05,
        },
        '单日熔断': {
            'mu': 0.0003, 'sigma': 0.012,
            'jump_lambda': 0.50,  # 极高跳跃频率
            'jump_mu': -0.15,    # 单日 -15%
            'jump_sigma': 0.05,
        },
    }

    print("=" * 65)
    print(f"{'场景':<20} {'夏普':>8} {'最大回撤':>10} {'年化收益':>10}")
    print("-" * 65)

    for name, params in scenarios.items():
        # 每场景跑 50 次 Monte Carlo
        sharpes, dds, rets = [], [], []
        for _ in range(50):
            prices = jump_diffusion_generator(**params)
            signal = double_ma_strategy(prices)
            res = backtest_with_costs(prices, signal)
            sharpes.append(res['sharpe'])
            dds.append(res['max_drawdown'])
            rets.append(res['annual_return'])

        print(f"{name:<20} {np.mean(sharpes):>8.2f} "
              f"{np.mean(dds):>10.2%} {np.mean(rets):>10.2%}")

    print("\n解读:")
    print("- 策略在不同市场环境下表现差异极大")
    print("- 如果某场景下最大回撤>30%,实盘应主动降仓位")

stress_test_scenarios()
