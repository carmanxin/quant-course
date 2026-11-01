# @quantlab/output: 30a56e33
def verify_synthetic_vs_historical():
    """验证合成数据的统计特征是否匹配历史数据"""

    # 1. 加载一段真实历史数据(以 SPY 为例,2014-2024)
    # 这里模拟一段历史数据(实际使用时用 yfinance 或 tushare)
    np.random.seed(123)
    n_days = 2520
    dates = pd.bdate_range('2014-01-01', periods=n_days)

    # 模拟 SPY 的真实数据(均值 8% 年化,波动 15%)
    hist_returns = np.random.normal(0.0004, 0.0098, n_days)
    hist_prices = 200 * np.exp(np.cumsum(hist_returns))
    hist_series = pd.Series(hist_prices, index=dates, name='SPY_Historical')

    # 2. 用相同参数生成 100 组合成数据
    n_synthetic = 100
    synth_stats = {k: [] for k in ['ann_return', 'ann_vol', 'max_dd']}

    for i in range(n_synthetic):
        synth = heston_generator(
            n_days=n_days, mu=0.0004, v0=0.015**2,
            kappa=2.0, theta=0.015**2, xi=0.3, rho=-0.7
        )
        stats = compute_statistics(synth)
        synth_stats['ann_return'].append(float(stats['均值(年化)'].rstrip('%')) / 100)
        synth_stats['ann_vol'].append(float(stats['波动(年化)'].rstrip('%')) / 100)
        synth_stats['max_dd'].append(float(stats['最大回撤'].rstrip('%')) / 100)

    # 3. 比较
    hist_stats = compute_statistics(hist_series)
    print("=" * 50)
    print("历史数据 vs Heston 合成数据对比")
    print("=" * 50)
    print(f"{'指标':<15} {'历史':>12} {'合成均值':>12} {'合成标准差':>12}")
    print("-" * 50)
    print(f"{'年化收益':<15} {hist_stats['均值(年化)']:>12} "
          f"{np.mean(synth_stats['ann_return'])*100:>10.2f}% "
          f"{np.std(synth_stats['ann_return'])*100:>10.2f}%")
    print(f"{'年化波动':<15} {hist_stats['波动(年化)']:>12} "
          f"{np.mean(synth_stats['ann_vol'])*100:>10.2f}% "
          f"{np.std(synth_stats['ann_vol'])*100:>10.2f}%")
    print(f"{'最大回撤':<15} {hist_stats['最大回撤']:>12} "
          f"{np.mean(synth_stats['max_dd'])*100:>10.2f}% "
          f"{np.std(synth_stats['max_dd'])*100:>10.2f}%")

    print("\n结论:合成数据统计特征应与历史数据在均值±2σ范围内。")
    print("      如果差异过大,需要重新拟合模型参数。")

verify_synthetic_vs_historical()
