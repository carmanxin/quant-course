# @quantlab/output: 60dfb1cb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple


def trend_following_strategy(returns: pd.Series, fast: int = 10, slow: int = 50) -> pd.Series:
    """趋势策略:动量
    短均线上穿长均线 → 持有,下穿 → 空仓
    """
    prices = (1 + returns).cumprod()
    fast_ma = prices.rolling(fast).mean()
    slow_ma = prices.rolling(slow).mean()
    signal = (fast_ma > slow_ma).astype(int).shift(1).fillna(0)
    return signal


def mean_reversion_strategy(returns: pd.Series, window: int = 20) -> pd.Series:
    """均值回归策略:反向
    短期大幅下跌后买入,反弹后卖出
    """
    prices = (1 + returns).cumprod()
    r = prices.pct_change()
    z_score = (r - r.rolling(window).mean()) / r.rolling(window).std()
    signal = (z_score < -1.5).astype(int).shift(1).fillna(0)
    return signal


def long_short_strategy(returns: pd.Series, half_life: int = 30) -> pd.Series:
    """套利(长短腿)风格策略:横截面动量
    假设有多只股票池,做多强势做空弱势。这里用绝对动量近似
    """
    prices = (1 + returns).cumprod()
    momentum = prices.pct_change(half_life)
    signal = (momentum > 0).astype(int).shift(1).fillna(0)
    return signal


def compute_strategy_returns(returns: pd.Series, signal: pd.Series,
                            fee: float = 0.0003) -> pd.Series:
    """根据持仓信号计算策略净收益(扣除成本)"""
    str_returns = returns * signal
    turnover = signal.diff().abs().fillna(signal.iloc[0]) * fee
    return str_returns - turnover


def generate_correlated_returns(n_days: int = 1260,
                                n_assets: int = 1,
                                true_sharpe: float = 1.0,
                                vol: float = 0.02,
                                regime: str = 'normal') -> pd.Series:
    """生成一段 Heston 风格的收益序列,确保三个策略在其中表现有差异"""
    np.random.seed(0)
    dates = pd.bdate_range('2020-01-01', periods=n_days)

    # 模拟不同 regime
    if regime == 'normal':
        # 正常市场:动量有效,均值回归震荡
        n = n_days
        v = vol**2
        r = np.random.normal(0.0005, vol, n)
    elif regime == 'trending':
        # 强趋势:动量大胜
        r = np.concatenate([
            np.cumsum(np.random.normal(0.003, 0.015, n_days // 2)),
            np.cumsum(np.random.normal(0.0005, 0.015, n_days // 2)),
        ]) - np.concatenate([
            np.zeros(n_days // 2),
            np.full(n_days // 2, np.random.uniform(0.5, 1.5)),
        ])
    else:
        r = np.random.normal(-0.0005, 0.03, n_days)

    return pd.Series(r, index=dates, name='underlying_returns')


# ============================================================
# 模拟 3 个不同风格的策略
# ============================================================

np.random.seed(42)
n_days = 1260
dates = pd.bdate_range('2020-01-01', periods=n_days)

# 构造 3 个独立的资产,使其风格不同
# (这样我们做组合时,有"分散化空间")
def gen_independent_returns(n_days, mean, vol, seed):
    np.random.seed(seed)
    return pd.Series(
        np.random.normal(mean, vol, n_days),
        index=dates,
        name=f'asset_{seed}'
    )

asset_trend = gen_independent_returns(n_days, 0.0008, 0.018, 1)   # 高均值低波动 → 趋势行情
asset_meanrev = gen_independent_returns(n_days, 0.0003, 0.025, 2)  # 中等 → 均值回归震荡
asset_ls = gen_independent_returns(n_days, 0.0005, 0.022, 3)       # 中等 → 套利风格

# 计算三策略各自的持仓信号和净收益
signal_trend = trend_following_strategy(asset_trend)
signal_meanrev = mean_reversion_strategy(asset_meanrev)
signal_ls = long_short_strategy(asset_ls)

ret_trend = compute_strategy_returns(asset_trend, signal_trend)
ret_meanrev = compute_strategy_returns(asset_meanrev, signal_meanrev)
ret_ls = compute_strategy_returns(asset_ls, signal_ls)

returns_df = pd.DataFrame({
    'Trend': ret_trend,
    'MeanRev': ret_meanrev,
    'LongShort': ret_ls,
})
print("3 个策略的相关性矩阵:")
print(returns_df.corr().round(3))

# ============================================================
# 计算单策略绩效
# ============================================================

def perf_stats(returns: pd.Series, label: str = 'Series') -> Dict[str, float]:
    equity = (1 + returns).cumprod()
    total_return = equity.iloc[-1] - 1
    ann_return = (1 + total_return) ** (252 / len(returns)) - 1
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    max_dd = (equity / equity.cummax() - 1).min()
    return {
        f'{label} - 总收益': f"{total_return:.2%}",
        f'{label} - 夏普': f"{sharpe:.2f}",
        f'{label} - 最大回撤': f"{max_dd:.2%}",
        f'{label} - 年化波动': f"{ann_vol:.2%}",
    }


print("\n" + "=" * 50)
print("单策略表现")
print("=" * 50)
for col in returns_df.columns:
    stats = perf_stats(returns_df[col], col)
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print()
