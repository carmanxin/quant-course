# @quantlab/output: dc6be893
def double_ma_strategy(prices: pd.Series,
                       fast: int = 10,
                       slow: int = 50) -> pd.Series:
    """简单双均线策略:返回每日持仓(1=持仓,0=空仓)"""
    fast_ma = prices.rolling(fast).mean()
    slow_ma = prices.rolling(slow).mean()
    signal = (fast_ma > slow_ma).astype(int).shift(1).fillna(0)
    return signal


def backtest_with_costs(prices: pd.Series, signal: pd.Series,
                        fee_rate: float = 0.0003,
                        slippage: float = 0.0005) -> Dict[str, float]:
    """带交易成本的简单回测"""
    returns = prices.pct_change().fillna(0)
    positions = signal

    # 策略收益
    strategy_returns = returns * positions

    # 换手率(每根 K 线仓位变化的绝对值除以 2 = 实际交易)
    turnover = positions.diff().abs().fillna(positions.iloc[0]) / 2

    # 扣除交易成本(单边费率:佣金+滑点)
    cost_returns = turnover * (fee_rate + slippage) * 2
    strategy_returns = strategy_returns - cost_returns

    # 计算绩效
    equity = (1 + strategy_returns).cumprod()
    total_return = equity.iloc[-1] - 1
    annual_return = (1 + total_return) ** (252 / len(equity)) - 1
    annual_vol = strategy_returns.std() * np.sqrt(252)
    sharpe = annual_return / annual_vol if annual_vol > 0 else 0
    max_dd = (equity / equity.cummax() - 1).min()

    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'annual_vol': annual_vol,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'turnover': turnover.sum() / len(turnover),
    }


def monte_carlo_test(generator_func, **gen_kwargs):
    """Monte Carlo 测试:用 100 组合成数据测策略稳健性"""
    n_simulations = 100
    results = []

    for sim in range(n_simulations):
        prices = generator_func(**gen_kwargs)
        signal = double_ma_strategy(prices, fast=10, slow=50)
        result = backtest_with_costs(prices, signal)
        results.append(result)

    results_df = pd.DataFrame(results)
    summary = {
        '夏普 - 均值': results_df['sharpe'].mean(),
        '夏普 - 中位数': results_df['sharpe'].median(),
        '夏普 - 标准差': results_df['sharpe'].std(),
        '夏普 - 最小': results_df['sharpe'].min(),
        '夏普 - 最大': results_df['sharpe'].max(),
        '夏普 - 5%分位数': results_df['sharpe'].quantile(0.05),
        '夏普 - 95%分位数': results_df['sharpe'].quantile(0.95),
        '胜率(>0)': (results_df['total_return'] > 0).mean(),
        '平均最大回撤': results_df['max_drawdown'].mean(),
    }
    return summary, results_df


print("\n" + "=" * 70)
print("Monte Carlo 仿真:双均线策略在 4 种合成数据上的稳健性")
print("=" * 70)

summary, _ = monte_carlo_test(gbm_generator)
print("\nGBM (100 组仿真):")
for k, v in summary.items():
    print(f"  {k}: {v:.3f}")

summary, _ = monte_carlo_test(heston_generator)
print("\nHeston (100 组仿真):")
for k, v in summary.items():
    print(f"  {k}: {v:.3f}")

summary, _ = monte_carlo_test(jump_diffusion_generator)
print("\nJumpDiff (100 组仿真):")
for k, v in summary.items():
    print(f"  {k}: {v:.3f}")

summary, _ = monte_carlo_test(bates_generator)
print("\nBates (100 组仿真):")
for k, v in summary.items():
    print(f"  {k}: {v:.3f}")
