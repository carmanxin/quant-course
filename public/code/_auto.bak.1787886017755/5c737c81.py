# @quantlab/output: 5c737c81
import itertools

def optimize_ma_params(df, short_range=range(5, 55, 5), long_range=range(30, 210, 10)):
    """
    遍历参数空间，寻找最优的均线组合
    同时输出参数稳定性分析
    """
    results = []
    for s, l in itertools.product(short_range, long_range):
        if s >= l:
            continue
        result = dual_ma_strategy(df, short_window=s, long_window=l)
        # 计算绩效指标
        rets = result['strategy_returns'].dropna()
        sharpe = rets.mean() / rets.std() * np.sqrt(252)
        max_dd = (result['cumulative_strategy'].cummax() -
                  result['cumulative_strategy']).max()
        results.append({
            'short': s, 'long': l,
            'sharpe': sharpe,
            'max_dd': max_dd,
            'total_return': result['cumulative_strategy'].iloc[-1] - 1
        })

    results_df = pd.DataFrame(results)

    # 最优组合
    best = results_df.loc[results_df['sharpe'].idxmax()]
    print(f"最优参数: short={int(best['short'])}, long={int(best['long'])}")
    print(f"最优夏普: {best['sharpe']:.2f}")

    # 参数敏感性：夏普比率的热力图
    pivot = results_df.pivot_table(
        values='sharpe', index='short', columns='long'
    )

    return results_df, pivot
