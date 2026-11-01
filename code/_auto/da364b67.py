# @quantlab/output: da364b67
def simulate_kelly_strategy(returns, kelly_fraction=1.0, rebalance_freq='monthly'):
    """
    模拟使用凯利准则分配资金的策略表现

    Parameters:
        returns: pd.Series, 日收益率
        kelly_fraction: 凯利分数（0.5=half-kelly, 1.0=full-kelly）
        rebalance_freq: 再平衡频率
    """
    # 估计参数（滚动回看窗口）
    lookback = 252
    mu_rolling = returns.rolling(lookback).mean() * 252
    sigma_rolling = returns.rolling(lookback).std() * np.sqrt(252)

    # 计算凯利杠杆
    kelly_leverage = (mu_rolling / (sigma_rolling ** 2)).shift(1)
    kelly_leverage = kelly_leverage.clip(lower=0, upper=5)  # 限制最大杠杆
    kelly_leverage = kelly_leverage * kelly_fraction

    # 策略收益
    strategy_returns = returns * kelly_leverage

    # 净值曲线
    equity = (1 + strategy_returns).cumprod()

    return equity, kelly_leverage

def kelly_vs_fixed_comparison(returns):
    """
    对比不同凯利分数的长期表现
    """
    fractions = [0.25, 0.5, 0.75, 1.0]
    results = {}

    for frac in fractions:
        equity, leverage = simulate_kelly_strategy(returns, kelly_fraction=frac)

        total_ret = equity.iloc[-1] - 1
        dd = (equity.cummax() - equity) / equity.cummax()
        max_dd = dd.max()

        results[f'Kelly-{frac*100:.0f}%'] = {
            '总收益': f'{total_ret:.1%}',
            '最大回撤': f'{max_dd:.1%}',
            '平均杠杆': f'{leverage.mean():.2f}x',
            '最大杠杆': f'{leverage.max():.2f}x',
        }

    return pd.DataFrame(results).T
