# @quantlab/output: 9ee5cbcb
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict


def generate_test_data(n_days: int = 2000) -> pd.Series:
    """生成一段 Heston 风格的合成价格序列(让双均线策略有可优化的空间)"""
    np.random.seed(42)
    dates = pd.bdate_range('2016-01-01', periods=n_days)

    # 模拟不同 regime:前 1000 天是趋势,后 1000 天震荡
    mu_regime = np.concatenate([
        np.full(1000, 0.0008),
        np.full(n_days - 1000, -0.0002),
    ])
    sigma_regime = np.concatenate([
        np.full(1000, 0.015),
        np.full(n_days - 1000, 0.025),
    ])

    returns = np.zeros(n_days)
    for i in range(1, n_days):
        returns[i] = np.random.normal(mu_regime[i], sigma_regime[i])
    prices = 100 * np.exp(np.cumsum(returns))
    return pd.Series(prices, index=dates, name='Price')


def double_ma_backtest(prices: pd.Series, fast: int, slow: int,
                        fee_rate: float = 0.0003) -> Dict[str, float]:
    """单次回测:给定 fast/slow,返回 Sharpe、收益、回撤"""
    fast_ma = prices.rolling(fast).mean()
    slow_ma = prices.rolling(slow).mean()
    signal = (fast_ma > slow_ma).astype(int).shift(1).fillna(0)

    returns = prices.pct_change().fillna(0)
    turnover = signal.diff().abs().fillna(signal.iloc[0]) * fee_rate
    str_returns = returns * signal - turnover

    equity = (1 + str_returns).cumprod()
    total_return = equity.iloc[-1] - 1
    n_days = len(equity)
    ann_return = (1 + total_return) ** (252 / n_days) - 1
    ann_vol = str_returns.std() * np.sqrt(252)
    sharpe = ann_return / (ann_vol + 1e-9)
    max_dd = (equity / equity.cummax() - 1).min()

    return {
        'fast': fast, 'slow': slow,
        'sharpe': sharpe,
        'ann_return': ann_return,
        'max_drawdown': max_dd,
        'turnover': turnover.sum() / n_days,
    }


def walk_forward_optimization(prices: pd.Series,
                              train_window: int = 504,    # 2 年训练
                              test_window: int = 126,     # 6 月测试
                              step: int = 63,              # 滚动 3 月
                              fast_grid: List[int] = None,
                              slow_grid: List[int] = None,
                              fee_rate: float = 0.0003) -> Dict:
    """Walk-Forward 优化主函数"""
    if fast_grid is None:
        fast_grid = list(range(5, 30, 5))
    if slow_grid is None:
        slow_grid = list(range(20, 100, 10))

    # 候选参数组合
    param_combos = [(f, s) for f in fast_grid for s in slow_grid if f < s]

    n = len(prices)
    wf_results = []
    chosen_params = []
    all_train_results = []  # 用于 decay 分析

    i = 0
    while i + train_window + test_window <= n:
        # 切片
        train_data = prices.iloc[i:i + train_window]
        test_data = prices.iloc[i + train_window:i + train_window + test_window]

        # 在训练期内找最优参数
        best_sharpe = -np.inf
        best_params = None
        for f, s in param_combos:
            res = double_ma_backtest(train_data, f, s, fee_rate)
            if res['sharpe'] > best_sharpe:
                best_sharpe = res['sharpe']
                best_params = (f, s)
                best_train_result = res

        # 在测试期验证
        if best_params is not None:
            test_result = double_ma_backtest(test_data, best_params[0],
                                              best_params[1], fee_rate)
            wf_results.append({
                'window_idx': i // step,
                'train_start': train_data.index[0],
                'train_end': train_data.index[-1],
                'test_start': test_data.index[0],
                'test_end': test_data.index[-1],
                'best_fast': best_params[0],
                'best_slow': best_params[1],
                'train_sharpe': best_train_result['sharpe'],
                'test_sharpe': test_result['sharpe'],
                'train_return': best_train_result['ann_return'],
                'test_return': test_result['ann_return'],
                'test_drawdown': test_result['max_drawdown'],
            })
            chosen_params.append(best_params)

        i += step

    return {
        'wf_results': pd.DataFrame(wf_results),
        'chosen_params': chosen_params,
    }


# === 主程序 ===
prices = generate_test_data()
print(f"生成数据 {len(prices)} 天, 时间 {prices.index[0]} 到 {prices.index[-1]}")
print()

result = walk_forward_optimization(prices)
wf_df = result['wf_results']
print(f"总共完成 {len(wf_df)} 轮 Walk-Forward 验证")
print()

print("=" * 80)
print("Walk-Forward 详细报告")
print("=" * 80)
print(wf_df.round(3).to_string())

print("\n" + "=" * 50)
print("样本内 vs 样本外统计")
print("=" * 50)
print(f"训练期平均夏普: {wf_df['train_sharpe'].mean():.2f}")
print(f"测试期平均夏普: {wf_df['test_sharpe'].mean():.2f}")
print(f"夏普衰减率: {(1 - wf_df['test_sharpe'].mean() / wf_df['train_sharpe'].mean()):.2%}")
print(f"测试期胜率(>0): {(wf_df['test_sharpe'] > 0).mean():.2%}")
